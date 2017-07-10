from django.db import models
from taggit.managers import TaggableManager
from media_mgr.models import MediaObjects
from django.contrib.contenttypes import generic
from genericm2m.models import RelatedObjectsDescriptor
from location_mgr.models import LocationMgr
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from location_mgr.signals import location
from polymorphic.models import PolymorphicModel
from rabbit_service import rconfig
import pdb
from django.db.models import Q
from wizcardship.models import Wizcard
from lib.preserialize.serialize import serialize
from wizserver import verbs
from base.cctx import ConnectionContext
from django.conf import settings
from taganomy.models import Taganomy
from notifications.signals import notify
from base.char_trunc import TruncatingCharField
from base.mixins import Base414Mixin
import pdb


# Create your models here.

class BaseEntityManager(models.Manager):

    def create(self, *args, **kwargs):
        category = kwargs.pop('category', Taganomy.objects.get_default_category())
        return super(BaseEntityManager, self).create(*args, category=category, **kwargs)

    def get_location_tree_name(self, etype):
        if etype == BaseEntity.TABLE:
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


# everything inherits from this.
class BaseEntityComponent(PolymorphicModel):
    owners = models.ManyToManyField(
        User,
        through='BaseEntityComponentsUser',
        related_name="owners_%(class)s_related"
    )

    @classmethod
    def create(cls, e, owner, is_creator, **kwargs):
        obj = e.objects.create(**kwargs)

        # add owner
        BaseEntityComponentsUser.objects.create(
            base_entity=obj,
            user=owner,
            is_creator=is_creator
        )

        return obj

    @classmethod
    def add_creator(cls, obj, creator):
        BaseEntityComponentsUser.objects.create(
            base_entity=obj,
            user=creator,
            is_creator=True
        )

    @classmethod
    def add_owners(cls, obj, owners):
        for o in owners:
            BaseEntityComponentsUser.objects.create(
                base_entity=obj,
                user=o,
                is_creator=False
            )

    def remove_owners(self, obj, owners):
        for o in owners:
            BaseEntityComponentsUser.objects.filter(
                base_entity=obj,
                user=o
            ).delete()


class BaseEntityComponentsUser(models.Model):
    base_entity = models.ForeignKey(BaseEntityComponent)
    user = models.ForeignKey(User)
    is_creator = models.BooleanField(default=True)


class BaseEntity(BaseEntityComponent, Base414Mixin):

    EVENT = 'EVT'
    BUSINESS = 'BUS'
    PRODUCT = 'PRD'
    TABLE = 'TBL'

    ENTITY_CHOICES = (
        (EVENT, 'Event'),
        (BUSINESS, 'Business'),
        (PRODUCT, 'Product'),
        (TABLE, 'Table'),
    )

    SUB_ENTITY_PRODUCT = 'e_product'
    SUB_ENTITY_TABLE = 'e_table'

    entity_type = models.CharField(
        max_length=3,
        choices=ENTITY_CHOICES,
        default=EVENT
    )

    secure = models.BooleanField(default=False)
    password = TruncatingCharField(max_length=40, blank=True)

    timeout = models.IntegerField(default=30)
    expired = models.BooleanField(default=False)
    is_activated = models.BooleanField(default=False)

    category = models.ForeignKey(Taganomy, blank=True)
    # media
    media = generic.GenericRelation(MediaObjects)

    # hashtags.
    tags = TaggableManager()

    users = models.ManyToManyField(
        User,
        through='UserEntity',
        related_name="users_%(class)s_related"
    )

    num_users = models.IntegerField(default=1)

    engagements = models.OneToOneField(
        "EntityEngagementStats",
        null=True,
        related_name="engagements_%(class)s_related"
    )

    # sub-entities. using django-generic-m2m package
    related = RelatedObjectsDescriptor()

    location = generic.GenericRelation(LocationMgr)

    objects = BaseEntityManager()

    def __unicode__(self):
        return self.entity_type + '.' + self.name

    @classmethod
    def entity_cls_ser_from_type(cls, entity_type=None, detail=False):
        from entity.serializers import EventSerializerL2, EventSerializerL1, \
            BusinessSerializer, TableSerializerL1, TableSerializerL2, EntitySerializerL2, \
            ProductSerializerL1, ProductSerializerL2
        if entity_type == cls.EVENT:
            c = Event
            s = EventSerializerL1
            if detail:
                s = EventSerializerL2
        elif entity_type == cls.PRODUCT:
            c = Product
            if detail:
                s = ProductSerializerL1
            else:
                s = ProductSerializerL2
        elif entity_type == cls.BUSINESS:
            c = Business
            s = BusinessSerializer
        elif entity_type == cls.TABLE:
            c = VirtualTable
            if detail:
                s = TableSerializerL2
            else:
                s = TableSerializerL1
        else:
            c = BaseEntity
            s = EntitySerializerL2

        return c, s

    @classmethod
    def entity_cls_from_subentity_type(cls, entity_type):
        if entity_type == cls.SUB_ENTITY_PRODUCT:
            c = Product
        elif type == cls.SUB_ENTITY_TABLE:
            c = VirtualTable
        else:
            c = BaseEntity

        return c

    def add_subentity(self, id, entity_type):
        pdb.set_trace()
        c = self.entity_cls_from_subentity_type(entity_type)
        obj = c.objects.get(id=id)

        return self.related.connect(obj, alias=type)

    def remove_sub_entity_of_type(self, id, entity_type):
        self.related.filter(object_id=id, alias=entity_type).delete()

    def get_sub_entities_of_type(self, entity_type):
        return self.related.filter(alias=entity_type).generic_objects()

    def get_creator(self):
        return BaseEntityComponentsUser.objects.filter(
            base_entity=self,
            is_creator=True
        ).get().user.profile.user

    def is_creator(self, user):
        return bool(user == self.get_creator())

    def is_owner(self, user):
        return bool(self.owners.all() & user.profile.baseuser.all())

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

    def get_tags(self, tags):
        return self.tags.names()

    def get_parent_entities(self ):
        return self.related.related_to().generic_objects()

    # get user's friends within the entity
    def users_friends(self, user, limit=None):
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
        #send notif to all members, just like join
        qs = self.users.exclude(id=sender.pk) if exclude else self.users.all()
        for u in qs:
            notify.send(
                sender,
                recipient=u,
                verb=verb,
                target=entity
            )

        return

    def get_banner(self):
        media_row = self.media.filter(media_sub_type='BNR')[0]
        #if media_element is null better to have a place holder but what event will not have a image (Bad event)!!!
        return media_row.media_element


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


class EventManager(BaseEntityManager):
    def lookup(self, lat, lng, n, etype=BaseEntity.EVENT, count_only=False):
        return super(EventManager, self).lookup(
            lat,
            lng,
            n,
            etype,
            count_only
        )

    def users_entities(self, user, entity_type=BaseEntity.EVENT, include_expired=False):
        return super(EventManager, self).users_entities(
            user,
            entity_type=entity_type,
            include_expired=include_expired
        )

class Event(BaseEntity):
    start = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField(auto_now_add=True)

    objects = EventManager()

    def join(self, user):
        super(Event, self).join(user)

        # do any event specific stuff here
        return

    def leave(self, user):
        super(Event, self).leave(user)

        return


class ProductManager(BaseEntityManager):
    def users_entities(self, user, entity_type=BaseEntity.PRODUCT, include_expired=False):
        return super(ProductManager, self).users_entities(
            user,
            entity_type=entity_type,
            include_expired=include_expired
        )

class Product(BaseEntity):

    objects = ProductManager()

    # this is a follow
    def join(self, user):
        super(Product, self).join(user)

        self.notify_all_users(
            user,
            verbs.WIZCARD_ENTITY_JOIN[0],
            self,
        )

        return

    # this is an un-follow. Will happen when product is either
    # deleted from rolodex or if there is a button on the campaign
    # to un-follow
    def leave(self, user):
        super(Product, self).leave(user)

        # send notif to all members, just like join
        self.notify_all_users(
            user,
            verbs.WIZCARD_ENTITY_LEAVE[0],
            self,
        )

        return


class BusinessManager(BaseEntityManager):
    def users_entities(self, user, entity_type=BaseEntity.BUSINESS, include_expired=False):
        return super(BusinessManager, self).users_entities(
            user,
            entity_type=entity_type,
            include_expired=include_expired
        )

class Business(BaseEntity):

    objects = BusinessManager()

    pass


class VirtualTableManager(BaseEntityManager):
    def users_entities(self, user, entity_type=BaseEntity.TABLE, include_expired=False):
        return super(VirtualTableManager, self).users_entities(
            user,
            entity_type=entity_type,
            include_expired=include_expired
        )

    def lookup(self, lat, lng, n, etype=BaseEntity.TABLE, count_only=False):
        return super(VirtualTableManager, self).lookup(
            lat,
            lng,
            n,
            etype,
            count_only
        )

    def serialize(self, tables, template):
        return serialize(tables, **template)

    def serialize_split(self, tables, user, template):
        created, joined, connected, others = self.split_table(tables, user)

        s = dict()
        if created:
            s['created'] = self.serialize(created, template)
        if joined:
            s['joined'] = self.serialize(joined, template)
        if connected:
            s['connected'] = self.serialize(connected, template)
        if others:
            s['others'] = self.serialize(others, template)
        return s

    def split_table(self, tables, user):
        created = []
        joined = []
        connected = []
        others = []
        for t in tables:
            if t.is_creator(user):
                created.append(t)
            elif t.is_joined(user):
                joined.append(t)
            elif Wizcard.objects.are_wizconnections(
                    user.wizcard,
                    t.get_creator().wizcard):
                connected.append(t)
            else:
                others.append(t)
        return created, joined, connected, others


class VirtualTable(BaseEntity):

    objects = VirtualTableManager()

    def join(self, user):
        super(VirtualTable, self).join(user)

        self.notify_all_users(
            user,
            verbs.WIZCARD_ENTITY_JOIN[0],
            self,
        )
        return

    def leave(self, user):
        super(VirtualTable, self).leave(user)

        self.notify_all_users(
            user,
            verbs.WIZCARD_ENTITY_LEAVE[0],
            self,
        )
        return

    def table_exchange(self, joinee):
        joined = self.users.all().exclude(id=joinee.id)
        wizcard1 = User.objects.get(id=joinee.pk).wizcard

        wizcards = map(lambda u: u.wizcard, joined)

        for wizcard2 in wizcards:
            cctx = ConnectionContext(asset_obj=self)
            Wizcard.objects.exchange(wizcard1, wizcard2, cctx)

        return self

    def join_table_and_exchange(self, user, password, skip_password=False):
        #check password
        if (not self.secure) or \
            (self.password == password) or skip_password:
            m, created = UserEntity.user_join(user=user, base_entity_obj=self)
            if not created:
                #somehow already a member
		        return self
            self.inc_numsitting()

            self.table_exchange(user)
        else:
            return None
        return self

    def delete(self, *args, **kwargs):
        #notify members of deletion (including self)
        verb = kwargs.pop('type', verbs.WIZCARD_TABLE_DESTROY[0])
        members = self.users.all()
        for member in members:
            notify.send(
                self.get_creator(),
                recipient=member,
                verb=verb,
                target=self)

        self.location.get().delete()

        if verb == verbs.WIZCARD_TABLE_TIMEOUT[0]:
            self.expired = True
            self.save()
        else:
            self.users.clear()
            super(VirtualTable, self).delete(*args, **kwargs)

    def time_remaining(self):
        if not self.expired:
            return self.location.get().timer.get().time_remaining()
        return 0


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
            self.agg_like_level = ((self.agg_like_level * self.like_count) - stat.like_level + level) / self.like_count
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


from django.dispatch import receiver
from django.db.models.signals import post_save


@receiver(post_save, sender=Event)
@receiver(post_save, sender=Product)
@receiver(post_save, sender=Business)
@receiver(post_save, sender=VirtualTable)
def create_engagement_stats(sender, instance, created, **kwargs):
    if created:
        e = EntityEngagementStats.objects.create()
        instance.engagements = e
        instance.save()
