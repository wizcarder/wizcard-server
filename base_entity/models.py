from django.db import models
from taggit.managers import TaggableManager
from django.contrib.contenttypes.fields import GenericRelation
from genericm2m.models import RelatedObjectsDescriptor
from location_mgr.models import LocationMgr
from django.core.exceptions import ObjectDoesNotExist
from location_mgr.signals import location
from polymorphic.models import PolymorphicModel, PolymorphicManager
from rabbit_service import rconfig
from django.db.models import Q
from django.conf import settings
from base.char_trunc import TruncatingCharField
from base.mixins import Base414Mixin
from django.contrib.auth.models import User
from notifications.signals import notify
from wizserver import verbs
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
import ushlex as shlex
import datetime
import pdb

# Create your models here.


class BaseEntityComponentManager(PolymorphicManager):
    def users_entities(self, user, **kwargs):
        return BaseEntity.objects.users_entities(user, **kwargs)

    def owners_entities(self, user, entity_type):
        if not entity_type:
            return user.owners_baseentitycomponent_related.all()

        cls, ser = BaseEntityComponent.entity_cls_ser_from_type(entity_type=entity_type)
        return user.owners_baseentitycomponent_related.all().instance_of(cls)

    def get_tagged_entities(self, tags, entity_type):
        if not entity_type:
            return BaseEntityComponent.objects.filter(tags__name__in=tags)
        cls, ser = BaseEntityComponent.entity_cls_ser_from_type(entity_type=entity_type)
        return cls.objects.filter(tags__name__in=tags)

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
            entities = self.filter(id__in=result, expired=False, is_deleted=False)
        return entities, count

    def owners_entities(self, user, entity_type=None):
        return BaseEntityComponent.objects.owners_entities(user, entity_type)

    # idea of kwargs is that caller can pass additional params to filter within the base_entity
    def users_entities(self, user, **kwargs):
        # All the kwargs entity_type was meant for the entity_filter now the kwargs is being used for UserEntity
        # Later if we want to change users_entities to filter by entity attributes this might have to change.
        # For e.g. give me all users_entities which are expiring soon Something to ponder about
        entity_type = kwargs.pop('entity_type', BaseEntityComponent.EVENT)

        ue = UserEntity.objects.select_related('entity').filter(entity__entity_type=entity_type, user=user, **kwargs)
        cls,ser = BaseEntityComponent.entity_cls_ser_from_type(entity_type)
        ids = map(lambda x:x.entity.id, ue)
        return cls.objects.filter(id__in=ids)




    def get_tagged_entities(self, tags, entity_type=None):
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
        cls, ser = BaseEntityComponent.entity_cls_ser_from_type(entity_type=entity_type)
        return cls.objects.annotate(rank=SearchRank(sv, q)).order_by('-rank')

    def combine_search(self, query, entity_type=None):
        rs = []
        entities = set(list(self.search_entities(query, entity_type)))
        tags = shlex.split(query)
        tagged_entities = set(list(self.get_tagged_entities(tags)))
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
    related = RelatedObjectsDescriptor()

    engagements = models.OneToOneField(
        "EntityEngagementStats",
        null=True,
        related_name="engagements_%(class)s_related"
    )

    tags = TaggableManager()

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
            inst, created = BaseEntityComponentsOwner.objects.get_or_create(
                base_entity_component=obj,
                owner=o.user,
                defaults={'is_creator': False}
            )

            if inst.is_creator:
                raise AssertionError("user %s is already owner of %s" % (o.user, obj))

    @classmethod
    def remove_owners(cls, obj, owners):
        for o in owners:
            BaseEntityComponentsOwner.objects.filter(
                base_entity_component=obj,
                owner=o.user
            ).delete()

    @classmethod
    def entity_cls_ser_from_type(cls, entity_type=None, detail=False):
        from entity.serializers import EventSerializerL2, EventSerializerL1, \
            TableSerializerL1, TableSerializerL2, EntitySerializer, \
            CampaignSerializerL1, CampaignSerializerL2, CoOwnersSerializer, \
            SpeakerSerializerL2, SponsorSerializerL2, SponsorSerializerL1, AttendeeInviteeSerializer, \
            ExhibitorInviteeSerializer, AgendaSerializer, AgendaItemSerializer, PollSerializer, PollSerializerL1
        from scan.serializers import ScannedEntitySerializer, BadgeTemplateSerializer
        from taganomy.serializers import TaganomySerializer
        from taganomy.models import Taganomy
        from entity.models import Event, Campaign, VirtualTable, \
            Speaker, Sponsor, AttendeeInvitee, ExhibitorInvitee, CoOwners, Agenda, AgendaItem
        from media_components.models import MediaEntities
        from media_components.serializers import MediaEntitiesSerializer
        from polls.models import Poll
        from scan.models import ScannedEntity, BadgeTemplate

        if entity_type == cls.EVENT:
            c = Event
            s = EventSerializerL2 if detail else EventSerializerL1
        elif entity_type == cls.CAMPAIGN:
            c = Campaign
            s = CampaignSerializerL2 if detail else CampaignSerializerL1
        elif entity_type == cls.TABLE:
            c = VirtualTable
            s = TableSerializerL2 if detail else TableSerializerL1
        elif entity_type == cls.ATTENDEE_INVITEE:
            c = AttendeeInvitee
            s = AttendeeInviteeSerializer
        elif entity_type == cls.EXHIBITOR_INVITEE:
            c = ExhibitorInvitee
            s = ExhibitorInviteeSerializer
        elif entity_type == cls.MEDIA:
            c = MediaEntities
            s = MediaEntitiesSerializer
        elif entity_type == cls.COOWNER:
            c = CoOwners
            s = CoOwnersSerializer
        elif entity_type == cls.SPEAKER:
            c = Speaker
            s = SpeakerSerializerL2
        elif entity_type == cls.SPONSOR:
            c = Sponsor
            s = SponsorSerializerL2 if detail else SponsorSerializerL1
        elif entity_type == cls.MEDIA:
            c = MediaEntities
            s = MediaEntitiesSerializer
        elif entity_type == cls.AGENDA:
            c = Agenda
            s = AgendaSerializer
        elif entity_type == cls.AGENDA_ITEM:
            c = AgendaItem
            s = AgendaItemSerializer
        elif entity_type == cls.POLL:
            c = Poll
            s = PollSerializer if detail else PollSerializerL1
        elif entity_type == cls.BADGE_TEMPLATE:
            c = BadgeTemplate
            s = BadgeTemplateSerializer
        elif entity_type == cls.SCANNED_USER:
            c = ScannedEntity
            s = ScannedEntitySerializer
        elif entity_type == cls.CATEGORY:
            c = Taganomy
            s = TaganomySerializer
        else:
            c = BaseEntityComponent
            s = EntitySerializer

        return c, s

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

    def add_subentities(self, ids, type):
        c = self.entity_cls_from_subentity_type(type)
        int_ids = map(lambda x: int(x), ids)

        objs = c.objects.filter(id__in=int_ids)
        for obj in objs:
            self.add_subentity_obj(obj, alias=type)

        return objs

    def add_subentity_obj(self, obj, alias):
        self.related.connect(obj, alias=alias)

        #post_connect needs from and to parts of connection to do something meaningful
        # even for notification it needs event to send notifications for e.g.
        obj.post_connect(self)
        return obj

    def remove_sub_entities_of_type(self, entity_type):
        self.related.filter(alias=entity_type).delete()

    def remove_sub_entity_of_type(self, id, entity_type):
        self.related.filter(object_id=id, alias=entity_type).delete()

    def get_sub_entities_of_type(self, entity_type):
        return self.related.filter(alias=entity_type).generic_objects()

    def get_sub_entities_id_of_type(self, entity_type):
        return list(self.related.filter(alias=entity_type).values_list('object_id', flat=True))

    def get_media_filter(self, type, sub_type):
        media = self.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_MEDIA)

        return [m for m in media if m.media_type in type and m.media_sub_type in sub_type]

    def get_parent_entities(self):
        return self.related.related_to().generic_objects()

    def get_parent_entities_by_contenttype_id(self, contenttype_id):
        return self.related.related_to().filter(parent_type_id=contenttype_id).generic_objects()

    def get_creator(self):
        return BaseEntityComponentsOwner.objects.filter(
            base_entity_component=self,
            is_creator=True
        ).get().owner.profile.user

    def is_creator(self, user):
        return bool(user == self.get_creator())

    def is_owner(self, user):
        return bool(self.owners.all() & user.profile.baseuser.all())

    # when a sub-entity gets related, it might want to do things like sending notifications
    # override this in the derived classes to achieve the same
    def post_connect(self, obj):
        pass

    def add_tags(self, taglist):
        self.tags.add(*taglist)

    def get_tags(self):
        return self.tags.names()

    def update_tags(self, taglist):
        return self.tags.set(*taglist)

    def modified_since(self, timestamp):
        return True


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

    expired = models.BooleanField(default=False)
    is_activated = models.BooleanField(default=False)
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

    def user_attach(self, user, state, notify=True):

        UserEntity.user_attach(user, self, state=state)
        if notify == True:
            if state == UserEntity.JOIN:
                self.num_users += 1
                self.save()
                self.notify_all_users(
                    user,
                    verbs.WIZCARD_ENTITY_JOIN,
                    self
                )

        return self

    def user_detach(self, user, state, notify=True):
        UserEntity.user_detach(user, self)
        if notify == True:
            if state == UserEntity.LEAVE:
                self.num_users -= 1
                self.save()
                self.notify_all_users(
                    user,
                    verbs.WIZCARD_ENTITY_LEAVE,
                    self
                )


    def is_joined(self, user):
        return bool(user.userentity_set.filter(entity=self, state=UserEntity.JOIN).exists())

    def is_pinned(self, user):
        return bool(user.userentity_set.filter(entity=self, state=UserEntity.PIN).exists())



    def get_users_after(self, timestamp):
        # AA: REVERT ME. Temp for app testing
        ue = UserEntity.get_entity_members(self)
        # ue = UserEntity.objects.filter(entity=self, created__gte=timestamp)
        #users = map(lambda u: u.user, ue)
        return ue

    def get_wizcard_users(self):
        users = UserEntity.get_entity_members(self)
        wiz_users = [x for x in users if hasattr(x, 'wizcard')]
        return wiz_users

    def notify_all_users(self, sender, notif_type, entity, exclude_sender=True):
        # send notif to all members, just like join

        users = UserEntity.get_entity_members(self)

        for u in users:
            if exclude_sender and u == sender:
                continue
            notify.send(
                sender,
                recipient=u,
                notif_type=notif_type[verbs.NOTIF_TYPE_IDX],
                verb=notif_type[verbs.VERB_IDX],
                target=entity
            )

    def get_banner(self):
        media_row = self.get_sub_entities_of_type(entity_type=BaseEntity.SUB_ENTITY_MEDIA)
        if media_row:
            return media_row.media_element

        return ""

    def make_live(self):
        self.is_activated = True
        self.save()

    def delete(self, *args, **kwargs):
        notif_tuple = kwargs.pop('type', verbs.WIZCARD_ENTITY_DELETE)

        self.notify_all_users(
            self.get_creator(),
            notif_tuple,
            self,
            exclude_sender=False
        )

        self.location.get().delete()

        if notif_tuple[0] == verbs.WIZCARD_ENTITY_EXPIRE[0]:
            self.expired = True
            self.save()
        else:
            self.related.all().delete()
            super(BaseEntity, self).delete(*args, **kwargs)

    def expire(self):
        self.delete(type=verbs.WIZCARD_ENTITY_EXPIRE)

    def modified_since(self, timestamp):
        return self.modified > timestamp



# explicit through table since we will want to associate additional
# fields as we go forward.
class UserEntity(models.Model):
    JOIN = 1
    PIN = 2
    LEAVE=3
    UNPIN=4

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
    def user_attach(cls, user, base_entity_obj, state=JOIN):
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



    @classmethod
    def get_entity_members(cls, base_entity_obj):
        users = UserEntity.objects.select_related('user').filter(entity=base_entity_obj,state=UserEntity.JOIN)
        return map(lambda x:x.user, users)



    # Join Table.
    # this will contain per user level stat


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

    def user_liked(self, user, level=EntityUserStats.MID_ENGAGEMENT_LEVEL):
        try:
            user_like = EntityUserStats.objects.get(
                user=user,
                stats=self,
            )
            like_level = user_like.like_level
            liked = True if like_level else False
            return liked, user_like.like_level
        except:
            return False, 0

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
