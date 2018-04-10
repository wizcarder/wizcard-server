from django.db import models
from taggit.managers import TaggableManager
from django.contrib.contenttypes.fields import GenericRelation
from genericm2m.models import RelatedObjectsDescriptor, RelatedObject
from location_mgr.models import LocationMgr
from django.core.exceptions import ObjectDoesNotExist
from location_mgr.signals import location
from polymorphic.models import PolymorphicModel, PolymorphicManager
from rabbit_service import rconfig
from django.conf import settings
from base.char_trunc import TruncatingCharField
from base.mixins import Base414Mixin
from django.contrib.auth.models import User
from notifications.signals import notify
from wizserver import verbs
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
import ushlex as shlex
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from taggit.models import TaggedItem
from base.mixins import JoinFieldsMixin

import itertools

import pdb

# Create your models here.


class WizcardRelatedField(RelatedObject, JoinFieldsMixin):
    def __unicode__(self):
        return unicode(u'%s related to %s ("%s:%s")' % (self.parent, self.object, self.alias, self.join_fields))


class BaseEntityComponentManager(PolymorphicManager):
    def users_entities(self, user, user_filter={}, entity_filter={}):
        return BaseEntity.objects.users_entities(user, user_filter=user_filter, entity_filter=entity_filter)

    def owners_entities(self, user, entity_type):
        if not entity_type:
            return user.owners_baseentitycomponent_related.all().distinct()

        cls = BaseEntityComponent.entity_cls_from_type(entity_type=entity_type)
        return user.owners_baseentitycomponent_related.all().instance_of(cls).exclude(
            entity_state=BaseEntityComponent.ENTITY_STATE_DELETED
        )

    def get_tagged_entities(self, tags, entity_type):
        content_type = BaseEntityComponent.content_type_from_entity_type(entity_type)
        t_entities = TaggedItem.objects.filter(
            tag__name__in=tags,
            content_type_id=content_type.id
        ).distinct().values_list('object_id', flat=True)

        return content_type.get_all_objects_for_this_type(id__in=t_entities)

    def notify_via_entity_parent(self, entity, notif_tuple, notif_operation):
        # get parent entities
        parents = entity.get_parent_entities()

        # Q broadcast notif. Target=parent, action_object=sub-entity, notif_type=EntityUpdate
        [
            notify.send(
                parent.get_creator(),
                # recipient is dummy
                recipient=parent.get_creator(),
                notif_tuple=notif_tuple,
                target=parent,
                action_object=entity,
                notif_operation=notif_operation
            ) for parent in parents if parent.is_active() & parent.is_floodable
        ]


class BaseEntityManager(BaseEntityComponentManager):
    def create(self, *args, **kwargs):
        return super(BaseEntityManager, self).create(*args, **kwargs)

    def get_location_tree_name(self, etype):
        if etype == BaseEntityComponent.TABLE:
            return rconfig.TREES[rconfig.VTREE]
        return rconfig.TREES[rconfig.ETREE]

    def lookup(self, lat, lng, n, etype, count_only=False):
        ttype = self.get_location_tree_name(etype)

        entities = []
        result, count = LocationMgr.objects.lookup(ttype, lat, lng, n)

        # convert result to query set result

        # AR: TODO: this is getting kludgy with multiple parameters. Best to have
        # REST API filters that portal can use
        if count and not count_only:
            entities = self.filter(id__in=result, entity_state=BaseEntityComponent.ENTITY_STATE_PUBLISHED)
            count = entities.count()

        return entities, count

    def owners_entities(self, user, entity_type=None):
        return BaseEntityComponent.objects.owners_entities(user, entity_type)

    # idea of kwargs is that caller can pass additional params to filter within the base_entity
    def users_entities(self, user, user_filter={}, entity_filter={}):
        entity_type = entity_filter.pop('entity_type')

        # argument expand entity_filter
        prefix = 'entity__'
        mod_filter = dict((prefix+k, v) for k, v in entity_filter.items())

        # merge with user_filter
        mod_filter.update(user_filter)

        ue = UserEntity.objects.select_related('entity').filter(
            entity__entity_type=entity_type,
            user=user,
            **mod_filter
        ).distinct()

        # when the param to get_real_instances is empty, it returns everything hence the if else:(
        entities = BaseEntity.objects.get_real_instances(map(lambda x: x.entity, ue)) if ue else []
        return entities

    def get_tagged_entities(self, tags, entity_type):
        return BaseEntityComponent.objects.get_tagged_entities(tags, entity_type)

    def query(self, query_str):
        # check names
        q1 = Q(name__istartswith=query_str)
        q2 = Q(tags__name__istartswith=query_str)

        entities = self.filter(q1 | q2)[0: settings.DEFAULT_MAX_LOOKUP_RESULTS]

        return entities, entities.count()

    def search_entities(self, query, entity_type=None):
        q = SearchQuery(query)
        sv = SearchVector('name', weight='A') + SearchVector('description', weight='B')
        if not entity_type:
            return BaseEntity.objects.annotate(rank=SearchRank(sv, q)).order_by('-rank')
        cls = BaseEntityComponent.entity_cls_from_type(entity_type=entity_type)
        return cls.objects.annotate(rank=SearchRank(sv, q)).order_by('-rank')

    def combine_search(self, query, entity_type=None):
        rs = []
        entities = set(list(self.search_entities(query, entity_type)))
        tags = shlex.split(query)
        tagged_entities = set(list(self.get_tagged_entities(tags, entity_type)))
        # This should rank higher as it has matched tags and name | description
        common = entities & tagged_entities
        # Remove entities that are common from entities (this could have matched name | description)
        res_entities = list(entities - common)
        # Remove entities that are common from tagged_entities
        res_tagged = list(tagged_entities - common)
        # Ranking is common -> entities (could have matched name  \ description) -> entities(that have matched tags)
        # One downside is that if an entity has matched in description but not in name that will be ranked higher than tag match.
        rs = list(common) + res_entities + res_tagged
        return rs, len(rs)


# everything inherits from this. This holds the relationship
# end-points for owners and related_entity.
class BaseEntityComponent(PolymorphicModel):
    EVENT = 'EVT'
    CAMPAIGN = 'CMP'
    TABLE = 'TBL'
    WIZCARD = 'WZC'
    SPEAKER = 'SPK'
    SPONSOR = 'SPN'
    MEDIA = 'MED'
    ATTENDEE_INVITEE = 'ATI'
    EXHIBITOR_INVITEE = 'EXI'
    COOWNER = 'COW'
    AGENDA = 'AGN'
    AGENDA_ITEM = 'AGI'
    POLL = 'POL'
    BADGE_TEMPLATE = 'BDG'
    SCANNED_USER = 'SCN'
    CATEGORY = 'CAT'

    SERIALIZER_L0 = 0
    SERIALIZER_L1 = 1
    SERIALIZER_L2 = 2
    SERIALIZER_FULL = 3

    ENTITY_CHOICES = (
        (EVENT, 'Event'),
        (CAMPAIGN, 'Campaign'),
        (TABLE, 'Table'),
        (WIZCARD, 'Wizcard'),
        (SPEAKER, 'Speaker'),
        (SPONSOR, 'Sponsor'),
        (COOWNER, 'Coowner'),
        (ATTENDEE_INVITEE, 'AttendeeInvitee'),
        (EXHIBITOR_INVITEE, 'ExhibitorInvitee'),
        (MEDIA, 'Media'),
        (COOWNER, 'Coowner'),
        (AGENDA, 'Agenda'),
        (AGENDA_ITEM, 'AgendaItem'),
        (POLL, 'Polls'),
        (BADGE_TEMPLATE, 'Badges'),
        (SCANNED_USER, 'Scans'),
        (CATEGORY, 'Category')
    )

    SUB_ENTITY_CAMPAIGN = 'e_campaign'
    SUB_ENTITY_TABLE = 'e_table'
    SUB_ENTITY_WIZCARD = 'e_wizcard'
    SUB_ENTITY_SPEAKER = 'e_speaker'
    SUB_ENTITY_SPONSOR = 'e_sponsor'
    SUB_ENTITY_MEDIA = 'e_media'
    SUB_ENTITY_COOWNER = 'e_coowner'
    SUB_ENTITY_AGENDA = 'e_agenda'
    SUB_ENTITY_POLL = 'e_poll'
    SUB_ENTITY_EXHIBITOR_INVITEE = 'e_exhibitor'
    SUB_ENTITY_ATTENDEE_INVITEE = 'e_attendee'
    SUB_ENTITY_BADGE_TEMPLATE = 'e_badge'
    SUB_ENTITY_SCANNED_USER = 'e_scan'
    SUB_ENTITY_CATEGORY = 'e_category'

    ENTITY_STATE_CREATED = "CRT"
    ENTITY_STATE_PUBLISHED = "PUB"
    ENTITY_STATE_EXPIRED = "EXP"
    ENTITY_STATE_DELETED = "DEL"

    ENTITY_STATE_CHOICES = (
        (ENTITY_STATE_CREATED, "Created"),
        (ENTITY_STATE_PUBLISHED, "Published"),
        (ENTITY_STATE_EXPIRED, "Expired"),
        (ENTITY_STATE_DELETED, "Deleted")
    )

    entity_types_mapping = {
        CAMPAIGN: SUB_ENTITY_CAMPAIGN,
        TABLE: SUB_ENTITY_TABLE,
        WIZCARD: SUB_ENTITY_WIZCARD,
        SPEAKER: SUB_ENTITY_SPEAKER,
        SPONSOR: SUB_ENTITY_SPONSOR,
        MEDIA: SUB_ENTITY_MEDIA,
        ATTENDEE_INVITEE: SUB_ENTITY_ATTENDEE_INVITEE,
        EXHIBITOR_INVITEE: EXHIBITOR_INVITEE,
        COOWNER: SUB_ENTITY_COOWNER,
        AGENDA: SUB_ENTITY_AGENDA,
        AGENDA_ITEM: SUB_ENTITY_AGENDA,
        POLL: SUB_ENTITY_POLL,
        BADGE_TEMPLATE: SUB_ENTITY_BADGE_TEMPLATE,
        SCANNED_USER: SUB_ENTITY_SCANNED_USER,
        CATEGORY: SUB_ENTITY_CATEGORY
    }

    # use this in overridden delete to know whether to remove or mark-deleted
    ENTITY_DELETE = 1
    ENTITY_EXPIRE = 2

    objects = BaseEntityComponentManager()

    entity_type = models.CharField(
        max_length=3,
        choices=ENTITY_CHOICES,
        default=EVENT
    )

    owners = models.ManyToManyField(
        User,
        through='BaseEntityComponentsOwner',
        related_name="owners_%(class)s_related"
    )

    # sub-entities. using django-generic-m2m package
    related = RelatedObjectsDescriptor(WizcardRelatedField)

    engagements = models.OneToOneField(
        "EntityEngagementStats",
        null=True,
        related_name="engagements_%(class)s_related"
    )

    tags = TaggableManager()

    entity_state = models.CharField(choices=ENTITY_STATE_CHOICES, default=ENTITY_STATE_CREATED, max_length=3)

    @classmethod
    def create(cls, e, owner, is_creator, **kwargs):
        obj = e.objects.create(**kwargs)

        # add owner
        BaseEntityComponentsOwner.objects.create(
            base_entity_component=obj,
            owner=owner,
            is_creator=is_creator
        )

        return obj

    """
    updates an existing entry, which was already created. This method
    may not really be required since creator is set during creation time
    itself
    """
    @classmethod
    def update_creator(cls, obj, creator):
        BaseEntityComponentsOwner.objects.get(
            base_entity_component=obj,
            owner=creator).update(is_creator=True)

    @classmethod
    def add_owners(cls, obj, owners):
        for o in owners:
            BaseEntityComponentsOwner.objects.get_or_create(
                base_entity_component=obj,
                owner=o.user,
                defaults={'is_creator': False}
            )

    @classmethod
    def remove_owners(cls, obj, owners):
        for o in owners:
            BaseEntityComponentsOwner.objects.filter(
                base_entity_component=obj,
                owner=o.user
            ).delete()

    @classmethod
    def entity_cls_from_type(cls, entity_type):
        from taganomy.models import Taganomy
        from entity.models import Event, Campaign, VirtualTable, \
            Speaker, Sponsor, AttendeeInvitee, ExhibitorInvitee, CoOwners, Agenda, AgendaItem
        from media_components.models import MediaEntities
        from polls.models import Poll
        from scan.models import ScannedEntity, BadgeTemplate

        if entity_type == cls.EVENT:
            return Event
        elif entity_type == cls.CAMPAIGN:
            return Campaign
        elif entity_type == cls.TABLE:
            return VirtualTable
        elif entity_type == cls.ATTENDEE_INVITEE:
            return AttendeeInvitee
        elif entity_type == cls.EXHIBITOR_INVITEE:
            return ExhibitorInvitee
        elif entity_type == cls.MEDIA:
            return MediaEntities
        elif entity_type == cls.COOWNER:
            return CoOwners
        elif entity_type == cls.SPEAKER:
            return Speaker
        elif entity_type == cls.SPONSOR:
            return Sponsor
        elif entity_type == cls.MEDIA:
            return MediaEntities
        elif entity_type == cls.AGENDA:
            return Agenda
        elif entity_type == cls.AGENDA_ITEM:
            return AgendaItem
        elif entity_type == cls.POLL:
            return Poll
        elif entity_type == cls.BADGE_TEMPLATE:
            return BadgeTemplate
        elif entity_type == cls.SCANNED_USER:
            return ScannedEntity
        elif entity_type == cls.CATEGORY:
            return Taganomy
        else:
            raise RuntimeError('invalid entity_type: %s', entity_type)

    @classmethod
    def entity_ser_from_type_and_level(cls, entity_type, level=SERIALIZER_FULL):
        from entity.serializers import EventSerializerL2, EventSerializer, EventSerializerL0, EventSerializerL1, \
            TableSerializerL1, TableSerializerL2, TableSerializer, \
            CampaignSerializerL1, CampaignSerializer, CampaignSerializerL2, CoOwnersSerializer, \
            SpeakerSerializerL2, SpeakerSerializer, SponsorSerializerL2, SponsorSerializerL1, SponsorSerializer, AttendeeInviteeSerializer, \
            ExhibitorInviteeSerializer, AgendaSerializer, AgendaSerializerL1, AgendaItemSerializer, PollSerializer, PollSerializerL1
        from scan.serializers import ScannedEntitySerializer, BadgeTemplateSerializer
        from entity.serializers import TaganomySerializer, TaganomySerializerL2
        from media_components.serializers import MediaEntitiesSerializer

        ser_mapping = {
            cls.EVENT: {
                cls.SERIALIZER_L0: EventSerializerL0,
                cls.SERIALIZER_L1: EventSerializerL1,
                cls.SERIALIZER_L2: EventSerializerL2,
                cls.SERIALIZER_FULL: EventSerializer
            },
            cls.CAMPAIGN: {
                cls.SERIALIZER_L0: CampaignSerializerL1,
                cls.SERIALIZER_L1: CampaignSerializerL1,
                cls.SERIALIZER_L2: CampaignSerializerL2,
                cls.SERIALIZER_FULL: CampaignSerializer
            },
            cls.TABLE: {
                cls.SERIALIZER_L0: TableSerializerL1,
                cls.SERIALIZER_L1: TableSerializerL1,
                cls.SERIALIZER_L2: TableSerializerL2,
                cls.SERIALIZER_FULL: TableSerializer
            },
            cls.ATTENDEE_INVITEE: {
                cls.SERIALIZER_FULL: AttendeeInviteeSerializer
            },
            cls.EXHIBITOR_INVITEE: {
                cls.SERIALIZER_FULL: ExhibitorInviteeSerializer
            },
            cls.MEDIA: {
                cls.SERIALIZER_FULL: MediaEntitiesSerializer
            },
            cls.COOWNER: {
                cls.SERIALIZER_FULL: CoOwnersSerializer
            },
            cls.SPEAKER: {
                cls.SERIALIZER_L0: SpeakerSerializerL2,
                cls.SERIALIZER_L1: SpeakerSerializerL2,
                cls.SERIALIZER_L2: SpeakerSerializerL2,
                cls.SERIALIZER_FULL: SpeakerSerializer
            },
            cls.SPONSOR: {
                cls.SERIALIZER_L0: SponsorSerializerL1,
                cls.SERIALIZER_L1: SponsorSerializerL1,
                cls.SERIALIZER_L2: SponsorSerializerL2,
                cls.SERIALIZER_FULL: SponsorSerializer
            },
            cls.AGENDA: {
                cls.SERIALIZER_L0: AgendaSerializer,
                cls.SERIALIZER_L1: AgendaSerializerL1,
                cls.SERIALIZER_L2: AgendaSerializerL1,
                cls.SERIALIZER_FULL: AgendaSerializerL1,
            },
            cls.AGENDA_ITEM: {
                cls.SERIALIZER_L0: AgendaItemSerializer,
                cls.SERIALIZER_L1: AgendaItemSerializer,
                cls.SERIALIZER_L2: AgendaItemSerializer,
                cls.SERIALIZER_FULL: AgendaItemSerializer
            },
            cls.POLL: {
                cls.SERIALIZER_L0: PollSerializerL1,
                cls.SERIALIZER_L1: PollSerializerL1,
                cls.SERIALIZER_L2: PollSerializer,
                cls.SERIALIZER_FULL: PollSerializer
            },
            cls.SCANNED_USER: {
                cls.SERIALIZER_FULL: ScannedEntitySerializer
            },
            cls.CATEGORY: {
                cls.SERIALIZER_L0: TaganomySerializerL2,
                cls.SERIALIZER_L1: TaganomySerializerL2,
                cls.SERIALIZER_L2: TaganomySerializerL2,
                cls.SERIALIZER_FULL: TaganomySerializer
            },
            cls.BADGE_TEMPLATE: {
                cls.SERIALIZER_FULL: BadgeTemplateSerializer
            }
        }

        return ser_mapping[entity_type][level]

    @classmethod
    def entity_cls_ser_from_type_level(cls, entity_type=None, level=SERIALIZER_FULL):
        c = cls.entity_cls_from_type(entity_type)
        s = cls.entity_ser_from_type_and_level(entity_type, level)

        return c, s

    @classmethod
    def content_type_from_entity_type(cls, entity_type):
        c = BaseEntityComponent.entity_cls_from_type(entity_type=entity_type)
        return ContentType.objects.get_for_model(c)

    @classmethod
    def sub_entity_type_from_entity_type(cls, entity_type):
        return cls.entity_types_mapping[entity_type]

    @classmethod
    def entity_cls_from_subentity_type(cls, entity_type):
        from entity.models import Campaign, VirtualTable, \
            Speaker, Sponsor, CoOwners, Agenda, ExhibitorInvitee, AttendeeInvitee
        from taganomy.models import Taganomy
        from media_components.models import MediaEntities
        from wizcardship.models import Wizcard
        from polls.models import Poll
        from scan.models import ScannedEntity, BadgeTemplate
        if entity_type == cls.SUB_ENTITY_CAMPAIGN:
            c = Campaign
        elif type == cls.SUB_ENTITY_TABLE:
            c = VirtualTable
        elif entity_type == cls.SUB_ENTITY_WIZCARD:
            c = Wizcard
        elif entity_type == cls.SUB_ENTITY_SPEAKER:
            c = Speaker
        elif entity_type == cls.SUB_ENTITY_SPONSOR:
            c = Sponsor
        elif entity_type == cls.SUB_ENTITY_MEDIA:
            c = MediaEntities
        elif entity_type == cls.SUB_ENTITY_COOWNER:
            c = CoOwners
        elif entity_type == cls.SUB_ENTITY_AGENDA:
            c = Agenda
        elif entity_type == cls.SUB_ENTITY_POLL:
            c = Poll
        elif entity_type == cls.SUB_ENTITY_EXHIBITOR_INVITEE:
            c = ExhibitorInvitee
        elif entity_type == cls.SUB_ENTITY_ATTENDEE_INVITEE:
            c = AttendeeInvitee
        elif entity_type == cls.SUB_ENTITY_SCANNED_USER:
            c = ScannedEntity
        elif entity_type == cls.SUB_ENTITY_BADGE_TEMPLATE:
            c = BadgeTemplate
        elif entity_type == cls.SUB_ENTITY_CATEGORY:
            c = Taganomy
        else:
            raise AssertionError("Invalid sub_entity %s" % entity_type)

        return c

    # this does not send notif
    def add_subentities(self, ids, type):
        if not ids:
            return []

        c = self.entity_cls_from_subentity_type(type)
        int_ids = map(lambda x: int(x), ids)

        objs = c.objects.filter(id__in=int_ids)
        for obj in objs:
            self.related.connect(obj, alias=type)

        return objs

    # this does not send notif
    def remove_subentities(self, ids, type):
        if not ids:
            return

        int_ids = map(lambda x: int(x), ids)

        self.related.filter(object_id__in=int_ids, alias=type).delete()

    # kind of tagonomy's pattern. add any new ones, remove those not in the list
    # this does not send notif
    def add_remove_sub_entities_of_type(self, ids, type):
        to_be_deleted_ids_qs = self.related.filter(alias=type)
        new_obj_ids = []

        for id in ids:
            if not to_be_deleted_ids_qs.filter(object_id=id).exists():
                new_obj_ids.append(id)
            to_be_deleted_ids_qs = to_be_deleted_ids_qs.exclude(object_id=id)

        # add the new ones
        self.add_subentities(new_obj_ids, type)

        # delete the rest
        to_be_deleted_ids_qs.delete()

    def add_subentity_obj(self, obj, alias, **kwargs):
        join_fields = kwargs.pop('join_fields', {})
        connection = self.related.connect(obj, alias=alias)

        connection.join_fields = join_fields
        connection.save()
        kwargs.update(notif_operation=verbs.NOTIF_OPERATION_CREATE)

        return obj.post_connect_remove(self, **kwargs)

    def remove_sub_entity_obj(self, obj, subentity_type, **kwargs):
        self.related.filter(object_id=obj.id, alias=subentity_type).delete()
        kwargs.update(notif_operation=verbs.NOTIF_OPERATION_DELETE)

        return obj.post_connect_remove(self, **kwargs)

    def get_sub_entities_gfk_of_type(self, **kwargs):
        return self.related.filter(**kwargs)

    def get_sub_entities_of_type(self, entity_type, **kwargs):
        exclude = kwargs.pop('exclude', [self.ENTITY_STATE_DELETED])

        subent = self.related.filter(alias=entity_type).generic_objects()
        return [se for se in subent if se.entity_state not in exclude]

    def get_sub_entities_id_of_type(self, entity_type, **kwargs):
        # Ideally we could have avoided the 2 iterations, but this is to ensure that the logic is consistent across 2 functions
        subent = self.get_sub_entities_of_type(entity_type, **kwargs)
        return [se.id for se in subent]

    def get_media_filter(self, type, sub_type):
        media = self.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_MEDIA)

        return [m for m in media if m.media_type in type and m.media_sub_type in sub_type]

    def get_parent_entities(self, **kwargs):
        exclude = kwargs.pop('exclude', [self.ENTITY_STATE_DELETED])

        parents = self.related.related_to().generic_objects()
        return [p for p in parents if p.entity_state not in exclude]

    def get_parent_entities_by_contenttype_id(self, contenttype_id, **kwargs):
        exclude = kwargs.pop('exclude', [self.ENTITY_STATE_DELETED])

        parents = self.related.related_to().filter(parent_type_id=contenttype_id).generic_objects()
        return [p for p in parents if p.entity_state not in exclude]

    # is the instance of the kind that has notifiable users
    @property
    def is_floodable(self):
        return False

    def get_creator(self):
        return BaseEntityComponentsOwner.objects.filter(
            base_entity_component=self,
            is_creator=True
        ).get().owner.profile.user

    def is_creator(self, user):
        return bool(user == self.get_creator())

    def is_owner(self, user):
        return bool(set(self.owners.all()) & set(user.profile.baseuser.all()))

    # when a sub-entity gets related, it might want to do things like sending notifications
    # override this in the derived classes to achieve the same
    def post_connect_remove(self, parent, **kwargs):
        notif_operation = kwargs.pop('notif_operation', verbs.NOTIF_OPERATION_CREATE)
        send_notif = kwargs.pop('send_notif', True)

        entity_state = BaseEntityComponent.ENTITY_STATE_CREATED if notif_operation == verbs.NOTIF_OPERATION_DELETE \
            else BaseEntityComponent.ENTITY_STATE_PUBLISHED

        self.set_entity_state(entity_state)

        if send_notif and parent.is_active():
            notify.send(
                self.get_creator(),
                # recipient is dummy
                recipient=self.get_creator(),
                notif_tuple=verbs.WIZCARD_ENTITY_UPDATE,
                target=parent,
                action_object=self,
                notif_operation=notif_operation
            )

        return send_notif

    def add_tags(self, taglist):
        self.tags.add(*taglist)

    def get_tags(self):
        return self.tags.names()

    def update_tags(self, taglist):
        return self.tags.set(*taglist)

    def modified_since(self, timestamp):
        return True

    def set_entity_state(self, state):
        self.entity_state = state
        self.save()

    def is_active(self):
        return bool(self.entity_state == BaseEntityComponent.ENTITY_STATE_PUBLISHED)

    def is_expired(self):
        return bool(self.entity_state == BaseEntityComponent.ENTITY_STATE_EXPIRED)

    def is_deleted(self):
        return bool(self.entity_state == BaseEntityComponent.ENTITY_STATE_DELETED)

    # nothing here, should be overridden in derived classes
    def user_state(self, user):
        return ""

    def delete(self, *args, **kwargs):
        type = kwargs.pop("type", BaseEntityComponent.ENTITY_DELETE)

        if type == BaseEntityComponent.ENTITY_EXPIRE:
            self.set_entity_state(BaseEntityComponent.ENTITY_STATE_EXPIRED)
        else:
            self.set_entity_state(BaseEntityComponent.ENTITY_STATE_DELETED)

    @property
    def push_name_str(self):
        entity_to_push_name_str = {
            self.EVENT: ' ',
            self.CAMPAIGN: ' Campaign ',
            self.TABLE: ' Table ',
            self.SPEAKER: ' Speaker ',
            self.SPONSOR: ' Sponsor ',
            self.MEDIA: ' Media ',
            self.AGENDA: ' Agenda ',
            self.POLL: ' Poll ',
        }
        return entity_to_push_name_str[self.entity_type] if self.entity_type in entity_to_push_name_str else " "

class BaseEntityComponentsOwner(models.Model):
    base_entity_component = models.ForeignKey(BaseEntityComponent)
    owner = models.ForeignKey(User)
    is_creator = models.BooleanField(default=True)

    class Meta:
        unique_together = (("base_entity_component", "owner"),)


class BaseEntity(BaseEntityComponent, Base414Mixin):
    secure = models.BooleanField(default=False)
    password = TruncatingCharField(max_length=40, blank=True, null=True)

    timeout = models.IntegerField(default=30)

    is_deleted = models.BooleanField(default=False)

    users = models.ManyToManyField(
        User,
        through='UserEntity',
        related_name="users_%(class)s_related"
    )

    num_users = models.IntegerField(default=0)

    location = GenericRelation(LocationMgr)

    objects = BaseEntityManager()

    def __unicode__(self):
        return self.entity_type + '.' + self.name

    def create_or_update_location(self, lat, lng):
        try:
            l = self.location.get()
            updated = l.do_update(lat, lng)
            return updated, l
        except ObjectDoesNotExist:
            updated = False
            # create
            l_tuple = location.send(sender=self, lat=lat, lng=lng,
                                    tree=BaseEntity.objects.get_location_tree_name(self.entity_type))
            return updated, l_tuple[0][1]

    # get user's friends within the entity
    def users_friends(self, user, limit=None):
        from wizcardship.models import Wizcard
        entity_wizcards = [w.wizcard for w in self.users.all().order_by('?') if hasattr(w, 'wizcard')]
        entity_friends = [x for x in entity_wizcards if Wizcard.objects.is_wizcard_following(x, user.wizcard)]

        return entity_friends[:limit]

    def user_attach(self, user, state, do_notify=True):

        UserEntity.user_attach(user, self, state=state)

        if do_notify:
            if hasattr(user, 'wizcard'):
                notify.send(
                    user,
                    # recipient is dummy
                    recipient=self.get_creator(),
                    notif_tuple=verbs.WIZCARD_ENTITY_ATTACH,
                    target=self,
                    action_object=user,
                    do_push=False
                )

            if state == UserEntity.JOIN:
                self.num_users += 1
                self.save()

        return self

    def user_detach(self, user, state, do_notify=True):
        UserEntity.user_detach(user, self)

        if do_notify:
            if hasattr(user, 'wizcard'):
                notify.send(
                    user,
                    # recipient is dummy
                    recipient=self.get_creator(),
                    notif_tuple=verbs.WIZCARD_ENTITY_DETACH,
                    target=self,
                    action_object=user,
                    do_push=False
                )

            if state == UserEntity.LEAVE:
                self.num_users -= 1
                self.save()

        return self

    # override. BaseEntity derived objects can have subscribers. This can be further
    # overridden in sub-entities if needed
    @property
    def is_floodable(self):
        return True

    # This is used to control if the entity needs to send serialized wizcards
    # as part of the serialized output. Presently we want to do this only for
    # Event.
    @property
    def send_wizcard_on_access(self):
        return False

    def is_joined(self, user):
        return bool(user.userentity_set.filter(entity=self, state=UserEntity.JOIN).exists())

    def user_state(self, user):
        # There can only be 1 entry per user per entity
        if user.userentity_set.filter(entity=self, user=user).exists():
            return user.userentity_set.get(entity=self, user=user).state

        return ""

    def get_users_after(self, timestamp):
        # AA: REVERT ME. Temp for app testing
        ue = UserEntity.objects.select_related('user').filter(entity=self)
        # ue = UserEntity.objects.filter(entity=self, created__gte=timestamp)

        # this won't (shouldn't cause db lookup since user is prefetched.
        users = map(lambda x: x.user, ue)

        return users

    def flood_set(self, **kwargs):
        ntuple = kwargs.pop('ntuple', None)
        sender = kwargs.pop('sender', None)

        flood_list = [x for x in self.users.all() if hasattr(x, 'wizcard')]

        # special case. Not nice. This (supress notif to sender) is the only
        # case presently (for NOTIF_ATTACH). If there are more, we should move
        # this to the ntuple dict.
        if ntuple and verbs.get_notif_type(ntuple) == verbs.NOTIF_ENTITY_ATTACH:
            # remove sender
            if sender in flood_list:
                flood_list.remove(sender)

        return flood_list

    def delete(self, *args, **kwargs):
        delete_type = kwargs.get('type', self.ENTITY_DELETE)

        if self.location.exists():
            self.location.get().delete()

        notif_tuple = verbs.WIZCARD_ENTITY_DELETE if delete_type == self.ENTITY_DELETE else verbs.WIZCARD_ENTITY_EXPIRE

        notify.send(
            self.get_creator(),
            recipient=self.get_creator(),
            notif_tuple=notif_tuple,
            target=self
        )

        super(BaseEntity, self).delete(*args, **kwargs)

    def do_expire(self, *args, **kwargs):
        kwargs.update(type=self.ENTITY_EXPIRE)
        self.delete(*args, **kwargs)

    def modified_since(self, timestamp):
        return self.modified > timestamp


# explicit through table since we will want to associate additional
# fields as we go forward.
class UserEntity(models.Model):
    JOIN = 1
    PIN = 2
    LEAVE = 3
    UNPIN = 4

    STATE_CHOICES = (
        (JOIN, 'Join'),
        (PIN, 'Pin'),
    )

    user = models.ForeignKey(User)
    entity = models.ForeignKey(BaseEntity)
    last_accessed = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    state = models.PositiveSmallIntegerField(default=0)

    @classmethod
    def user_attach(cls, user, base_entity_obj, state):
        usr_entity, created = UserEntity.objects.get_or_create(
            user=user,
            entity=base_entity_obj,
            defaults={'state': state}
        )

        # Can join a pinned event but cannot pin a joined event.
        if not created:
            usr_entity.state = state
            usr_entity.save()

        return usr_entity, created

    @classmethod
    def user_detach(cls, user, base_entity_obj):
        user.userentity_set.filter(entity=base_entity_obj).delete()

    @classmethod
    def user_member(cls, user, entity_obj, **kwargs):
        try:
            u = UserEntity.objects.get(user=user, entity=entity_obj, state=UserEntity.JOIN, **kwargs)
            return u, True
        except:
            return None, False

    def last_accessed_at(self, timestamp):
        self.last_accessed = timestamp
        self.save()


# Join Table.
# this will contain per user level stats
class EntityUserStats(models.Model):

    MIN_ENGAGEMENT_LEVEL = 0
    MAX_ENGAGEMENT_LEVEL = 10
    MID_ENGAGEMENT_LEVEL = 5

    user = models.ForeignKey(User)
    stats = models.ForeignKey('EntityEngagementStats')

    # thinking of a new way to show likes...on a scale of [1, 10]
    # higher the number, deeper the color..maybe we can throb the
    # heart also...:-)
    like_level = models.IntegerField(default=MID_ENGAGEMENT_LEVEL)
    following = models.BooleanField(default=False)
    viewed = models.BooleanField(default=False)

# the entity model will use this


class EntityEngagementStats(models.Model):
    like_count = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    follows = models.IntegerField(default=0)
    unfollows = models.IntegerField(default=0)
    agg_like_level = models.FloatField(default=EntityUserStats.MIN_ENGAGEMENT_LEVEL)

    users = models.ManyToManyField(
        User,
        through='EntityUserStats'
    )

    def user_liked(self, user):
        try:
            user_like = EntityUserStats.objects.get(
                user=user,
                stats=self,
            )
        except ObjectDoesNotExist:
            return False, 0

        like_level = user_like.like_level
        liked = True if like_level else False

        return liked, user_like.like_level

    def like(self, user, level=EntityUserStats.MID_ENGAGEMENT_LEVEL):
        stat, created = EntityUserStats.objects.get_or_create(
            user=user,
            stats=self,
            defaults={
                'like_level': level
            }
        )

        if created:
            self.like_count += 1
            self.agg_like_level = ((self.agg_like_level * (int(self.like_count) - 1)) + level) / int(self.like_count)
        else:
            self.agg_like_level = ((self.agg_like_level * self.like_count) -
                                   stat.like_level + level) / int(self.like_count)
            stat.like_level = level
            stat.save()

        self.save()

        return self.like_count, self.agg_like_level

    def viewed(self, user):
        EntityUserStats.objects.get_or_create(
            user=user,
            stats=self,
            defaults={
                'viewed': True
            }
        )

        self.views += 1
        self.save()

        return self.views

    def follow(self, user):
        EntityUserStats.objects.get_or_create(
            user=user,
            stats=self,
            defaults={
                'following': True
            }
        )

        self.follows += 1
        self.save()

        return self.follows

    def unfollow(self, user):
        stat = EntityUserStats.objects.get(
            user=user,
            stats=self
        )
        stat.following = False
        stat.save()

        self.unfollows += 1
        self.save()

        return self.unfollows
