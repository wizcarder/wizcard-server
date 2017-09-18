from django.db import models
from taggit.managers import TaggableManager
from django.contrib.contenttypes import generic
from genericm2m.models import RelatedObjectsDescriptor
from location_mgr.models import LocationMgr
from django.core.exceptions import ObjectDoesNotExist
from location_mgr.signals import location
from polymorphic.models import PolymorphicModel
from rabbit_service import rconfig
from django.db.models import Q
from django.conf import settings
from taganomy.models import Taganomy
from base.char_trunc import TruncatingCharField
from django.contrib.contenttypes.models import ContentType
from base.mixins import  Base414Mixin
from django.contrib.auth.models import User
from notifications.signals import notify
import pdb

# Create your models here.

class BaseEntityManager(models.Manager):
    def create(self, *args, **kwargs):
        category = kwargs.pop('category', Taganomy.objects.get_default_category())
        return super(BaseEntityManager, self).create(*args, category=category, **kwargs)

    def get_location_tree_name(self, etype):
        if etype == BaseEntityComponent.TABLE:
            return rconfig.TREES[rconfig.VTREE]
        return rconfig.TREES[rconfig.ETREE]

    def lookup(self, lat, lng, n, etype, count_only=False):
        ttype = self.get_location_tree_name(etype)

        entities = []
        result, count = LocationMgr.objects.lookup(ttype, lat, lng, n)

        #convert result to query set result
        if count and not count_only:
            entities = self.filter(id__in=result)
        return entities, count

    def users_entities(self, user, entity_type=None, include_expired=False):
        cls, ser = BaseEntity.entity_cls_ser_from_type(entity_type=entity_type)
        if include_expired:
            return user.users_baseentity_related.all().instance_of(cls)
        else:
            return user.users_baseentity_related.all().instance_of(cls).exclude(expired=True)

    def query(self, query_str):
        # check names
        q1 = Q(name__istartswith=query_str)
        q2 = Q(tags__name__istartswith=query_str)
        #
        entities = self.filter(q1 | q2)[0: settings.DEFAULT_MAX_LOOKUP_RESULTS]

        return entities, entities.count()


class BaseEntityComponentManager(models.Manager):
    pass

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
    ATTENDEE = 'ATT'
    COOWNER = 'COW'
    AGENDA = 'AGN'

    ENTITY_CHOICES = (
        (EVENT, 'Event'),
        (CAMPAIGN, 'Campaign'),
        (TABLE, 'Table'),
        (WIZCARD, 'Wizcard'),
        (SPEAKER, 'Speaker'),
        (SPONSOR, 'Sponsor'),
        (COOWNER, 'Coowner'),
        (ATTENDEE, 'Attendee'),
        (MEDIA, 'Media'),
        (COOWNER, 'Coowner'),
        (AGENDA, 'Agenda')
    )

    SUB_ENTITY_CAMPAIGN = 'e_campaign'
    SUB_ENTITY_TABLE = 'e_table'
    SUB_ENTITY_WIZCARD = 'e_wizcard'
    SUB_ENTITY_SPEAKER = 'e_speaker'
    SUB_ENTITY_SPONSOR = 'e_sponsor'
    SUB_ENTITY_MEDIA = 'e_media'
    SUB_ENTITY_COOWNER = 'e_coowner'
    SUB_ENTITY_AGENDA = 'e_agenda'

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
    def add_creator(cls, obj, creator):
        BaseEntityComponentsOwner.objects.filter(
            base_entity_component=obj,
            owner=creator).update(is_creator=True)

    @classmethod
    def add_owners(cls, obj, owners):
        for o in owners:
            BaseEntityComponentsOwner.objects.create(
                base_entity_component=obj,
                owner=o,
                is_creator=False
            )

    @classmethod
    def remove_owners(cls, obj, owners):
        for o in owners:
            BaseEntityComponentsOwner.objects.filter(
                base_entity_component=obj,
                owner=o
            ).delete()

    @classmethod
    def entity_cls_ser_from_type(cls, entity_type=None, detail=False):
        from entity.serializers import EventSerializerL2, EventSerializerL1, \
            TableSerializerL1, TableSerializerL2, EntitySerializer, \
            CampaignSerializerL1, CampaignSerializerL2, CoOwnersSerializer, \
            SpeakerSerializerL2, SponsorSerializerL2
        from entity.models import Event, Campaign, VirtualTable, \
            Speaker, Sponsor, AttendeeInvitee, ExhibitorInvitee, CoOwners
        from media_components.models import MediaEntities
        from media_components.serializers import MediaEntitiesSerializer

        if entity_type == cls.EVENT:
            c = Event
            s = EventSerializerL2 if detail else EventSerializerL1
        elif entity_type == cls.CAMPAIGN:
            c = Campaign
            s = CampaignSerializerL2 if detail else CampaignSerializerL1
        elif entity_type == cls.TABLE:
            c = VirtualTable
            s = TableSerializerL2 if detail else TableSerializerL1
        elif entity_type == cls.ATTENDEE:
            c = AttendeeInvitee
            s = AttendeeSerializer
        elif entity_type == cls.EXHIBITOR:
            c = ExhibitorInvitee
            s = ExhibitorSerializer
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
            s = SponsorSerializerL2
        elif entity_type == cls.MEDIA:
            c = MediaEntities
            s = MediaEntitiesSerializer
        else:
            c = BaseEntity
            s = EntitySerializer

        return c, s

    @classmethod
    def entity_cls_from_subentity_type(cls, entity_type):
        from entity.models import Campaign, VirtualTable, \
            Speaker, Sponsor, ExhibitorInvitee, CoOwners, Agenda
        from media_components.models import MediaEntities
        from wizcardship.models import Wizcard
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
        elif entity_type == cls.SUB_ENTITY_EXHIBITOR:
            c = ExhibitorInvitee
        elif entity_type == cls.SUB_ENTITY_COOWNER:
            c = CoOwners
        elif entity_type == cls.SUB_ENTITY_AGENDA:
            c = Agenda

        return c

    # AR: TO fix
    def add_subentity(self, id, type):
        c = self.entity_cls_from_subentity_type(type)
        return self.related.connect(
            c.objects.get(id=id),
            alias=type
        )

    def add_subentities(self, ids, type):
        c = self.entity_cls_from_subentity_type(type)
        int_ids = map(lambda x: int(x), ids)

        # AR: TODO Why try except ? id's should always be correct.
        try:
            objs = c.objects.filter(id__in=int_ids)
            for obj in objs:
                self.related.connect(obj, alias=type)
        except:
            pass

    def add_subentity_obj(self, obj):
        return self.related.connect(obj, alias=ContentType.objects.get_for_model(obj).name)

    # AR: TO fix
    def remove_sub_entity_of_type(self, id, entity_type):
        self.related.filter(object_id=id, alias=entity_type).delete()

    # AR: TO fix
    def get_sub_entities_of_type(self, entity_type):
        return self.related.filter(alias=entity_type).generic_objects()

    def get_sub_entities_id_of_type(self, entity_type):
        return self.related.filter(alias=entity_type).values_list('object_id', flat=True)

    def get_media_filter(self, type, sub_type):
        media = self.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_MEDIA)
        banners = []
        for med in media:
            if med.media_sub_type == sub_type and med.media_type == type:
                banners.append(med)
        return banners

    def get_parent_entities(self ):
        try:
            parents = self.related.related_to().generic_objects()
            return parents
        except:
            return None

    def get_creator(self):
        return BaseEntityComponentsOwner.objects.filter(
            base_entity_component=self,
            is_creator=True
        ).get().owner.profile.user

    def is_creator(self, user):
        return bool(user == self.get_creator())

    def is_owner(self, user):
        return bool(self.owners.all() & user.profile.baseuser.all())


class BaseEntityComponentsOwner(models.Model):
    base_entity_component = models.ForeignKey(BaseEntityComponent)
    owner = models.ForeignKey(User)
    is_creator = models.BooleanField(default=True)

class BaseEntity(BaseEntityComponent, Base414Mixin):
    secure = models.BooleanField(default=False)
    password = TruncatingCharField(max_length=40, blank=True, null=True)

    timeout = models.IntegerField(default=30)
    expired = models.BooleanField(default=False)
    is_activated = models.BooleanField(default=False)

    category = models.ForeignKey(Taganomy, blank=True)

    # hashtags.
    tags = TaggableManager()

    users = models.ManyToManyField(
        User,
        through='UserEntity',
        related_name="users_%(class)s_related"
    )

    num_users = models.IntegerField(default=1)

    location = generic.GenericRelation(LocationMgr)

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

    def add_tags(self, taglist):
        self.tags.clear()
        for tag in taglist:
            self.tags.add(tag)

    def get_tags(self):
        return self.tags.names()

    # get user's friends within the entity
    def users_friends(self, user, limit=None):
        from wizcardship.models import Wizcard
        entity_wizcards = [w.wizcard for w in self.users.all().order_by('?') if hasattr(w, 'wizcard')]
        entity_friends = [x for x in entity_wizcards if Wizcard.objects.is_wizcard_following(x, user.wizcard)]

        return entity_friends[:limit]

    def join(self, user):
        e, created = UserEntity.user_join(user=user, base_entity_obj=self)
        if created:
            self.num_users += 1
            self.save()

        return self

    def is_joined(self, user):
        return bool(self.users.filter(id=user.id).exists())

    def leave(self, user):
        UserEntity.user_leave(user, self)
        self.num_users -= 1
        self.save()

        return self

    def get_users_after(self, timestamp):
        # AA: REVERT ME. Temp for app testing
        ue = UserEntity.objects.filter(entity=self)
        #ue = UserEntity.objects.filter(entity=self, created__gte=timestamp)
        users = map(lambda u: u.user, ue)

        return users

    def notify_all_users(self, sender, verb, entity, exclude=True):
        # send notif to all members, just like join
        qs = self.users.exclude(id=sender.pk) if exclude else self.users.all()
        for u in qs:
            notify.send(
                sender,
                recipient=u,
                verb=verb,
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


# explicit through table since we will want to associate additional
# fields as we go forward.
class UserEntity(models.Model):
    user = models.ForeignKey(User)
    entity = models.ForeignKey(BaseEntity)
    last_accessed = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @classmethod
    def user_join(cls, user, base_entity_obj):
        return  UserEntity.objects.get_or_create(
            user=user,
            entity=base_entity_obj
        )

    @classmethod
    def user_leave(self, user, base_entity_obj):
        user.userentity_set.get(entity=base_entity_obj).delete()

    @classmethod
    def user_member(cls, user, entity_obj):
        try:
            u = UserEntity.objects.get(user=user, entity=entity_obj)
            return u, True
        except:
            return None, False

    def last_accessed_at(self, timestamp):
        self.last_accessed = timestamp
        self.save()

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
            self.agg_like_level = ((self.agg_like_level * (self.like_count - 1)) + level) / self.like_count
        else:
            self.agg_like_level = ((
                                   self.agg_like_level * self.like_count) - stat.like_level + level) / self.like_count
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
