from django.db import models
from taggit.managers import TaggableManager
from media_mgr.models import MediaObjects
from django.contrib.contenttypes import generic
from genericm2m.models import RelatedObjectsDescriptor
from location_mgr.models import LocationMgr
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from location_mgr.signals import location
from base.char_trunc import TruncatingCharField
from base.emailField import EmailField
from speaker.models import Speaker
from polymorphic.models import PolymorphicModel
from polymorphic.manager import PolymorphicManager
from rabbit_service import rconfig
import pdb
from django.db.models import Q
from wizcardship.models import Wizcard
from lib.preserialize.serialize import serialize
from wizserver import fields, verbs
from notifications.models import notify
from base.cctx import ConnectionContext
from django.conf import settings


import pdb

# Create your models here.

class BaseEntityManager(PolymorphicManager):

    def get_location_tree_name(self, etype):
        if etype == BaseEntity.TABLE:
            return rconfig.TREES[rconfig.VTREE]
        return rconfig.TREES[rconfig.ETREE]

    def lookup(self, cache_key, lat, lng, n, etype, count_only=False):
        ttype = self.get_location_tree_name(etype)

        tables = None
        result, count = LocationMgr.objects.lookup(cache_key, ttype, lat, lng, n)

        #convert result to query set result
        if count and not count_only:
            tables = map(lambda m: self.get(id=m), result)
        return tables, count

    def users_entities(self, user, include_expired=False):
        if include_expired:
            return user.users_baseentity_related.all()
        else:
            return user.users_baseentity_related.exclude(expired=True)


class BaseEntity(PolymorphicModel):

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

    entity_type = models.CharField(
        max_length=3,
        choices=ENTITY_CHOICES,
        default=EVENT
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    secure = models.BooleanField(default=False)
    timeout = models.IntegerField(default=30)
    expired = models.BooleanField(default=False)
    is_activated = models.BooleanField(default=False)

    name = models.CharField(max_length=100)
    address = models.CharField(max_length=80, blank=True)
    website = models.URLField()
    description = models.CharField(max_length=1000)
    phone = TruncatingCharField(max_length=20, blank=True)
    email = EmailField(blank=True)

    # media
    media = generic.GenericRelation(MediaObjects)

    # hashtags.
    tags = TaggableManager()

    creator = models.ForeignKey(User, related_name='created_%(class)s_related')

    owners = models.ManyToManyField(
        User,
        related_name="owners_%(class)s_related"
    )

    users = models.ManyToManyField(
        User,
        through='UserEntity',
        related_name="users_%(class)s_related"
    )

    # sub-entities. using django-generic-m2m package
    related = RelatedObjectsDescriptor()

    location = generic.GenericRelation(LocationMgr)

    objects = BaseEntityManager()

    def __unicode__(self):
        return self.entity_type + '.' + self.name

    @classmethod
    def get_entity_from_type(self, type):
        from entity.serializers import EventSerializer, ProductSerializer, BusinessSerializer, TableSerializer
        if type == self.EVENT:
            cls = Event
            serializer = EventSerializer
        elif type == self.PRODUCT:
            cls = Product
            serializer = ProductSerializer
        elif type == self.BUSINESS:
            cls = Business
            serializer = BusinessSerializer
        elif type == self.TABLE:
            cls = VirtualTable
            serializer = TableSerializer

        return cls, serializer

    def add_subentity(self, id, type):
        pass

    def remove_sub_entity_of_type(self, id, type):
        self.related.filter(object_id=id, alias=type).delete()

    def get_sub_entities_of_type(self, type):
        return self.related.filter(alias=type).generic_objects()

    def add_owner(self, obj):
        self.owners.add(obj)
        # AA:TODO: need to send owner a notif

    def remove_owner(self, obj):
        self.owners.remove(obj)
        # AA:TODO: need to send owner a notif

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



# explicit through table since we will want to associate additional
# fields as we go forward.
class UserEntity(models.Model):
    user = models.ForeignKey(User)
    entity = models.ForeignKey(BaseEntity)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @classmethod
    def user_join(self, user, entity_obj):
        return UserEntity.objects.get_or_create(
            user=user,
            entity=entity_obj.baseentity_ptr
        )

    @classmethod
    def user_leave(self, user, entity_obj):
        user.userentity_set.get(entity=entity_obj.baseentity_ptr).delete()


class EventManager(BaseEntityManager):

    def users_entities(self, user, include_expired=False):
        if include_expired:
            return user.users_baseentity_related.all().instance_of(Event)
        else:
            return user.users_baseentity_related.all().instance_of(Event).exclude(expired=True)

    def lookup(self, cache_key, lat, lng, n, count_only=False):
        from entity.serializers import EventSerializer, ProductSerializer, BusinessSerializer, TableSerializer
        flicked_cards = None
        result, count =  LocationMgr.objects.lookup(
            cache_key,
            "ETREE",
            lat,
            lng,
            n)
        #convert result to query set result
        if count and not count_only:
            events = EventSerializer(Event.objects.filter(id__in=result), many=True)
        return events, count


class Event(BaseEntity):
    SUB_ENTITY_PRODUCT = 'e_product'
    SUB_ENTITY_TABLE = 'e_table'

    start = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField(auto_now_add=True)
    speakers = models.ManyToManyField(Speaker, related_name='events')

    objects = EventManager()

    def create(self, *args, **kwargs):
        return super(Event, self).create(*args, entity_type=self.EVENT, **kwargs)

    def add_subentity(self, id, type):
        if type == self.SUB_ENTITY_PRODUCT:
            obj = Product.objects.get(id=id)
        elif type == self.SUB_ENTITY_TABLE:
            obj = VirtualTable.objects.get(id=id)

        return self.related.connect(obj, alias=type)

    def add_speaker(self, id):
        self.speakers.add(id)


class ProductManager(BaseEntityManager):

    def users_entities(self, user, include_expired=False):
        if include_expired:
            return user.users_baseentity_related.all().instance_of(Product)
        else:
            return user.users_baseentity_related.all().instance_of(Product).exclude(expired=True)


class Product(BaseEntity):

    def create(self, *args, **kwargs):
        return super(Event, self).create(*args, entity_type=self.PRODUCT, **kwargs)

    objects = ProductManager()

    pass


class BusinessManager(BaseEntityManager):

    def users_entities(self, user, include_expired=False):
        if include_expired:
            return user.users_baseentity_related.all().instance_of(Business)
        else:
            return user.users_baseentity_related.all().instance_of(Business).exclude(expired=True)


class Business(BaseEntity):

    def create(self, *args, **kwargs):
        return super(Event, self).create(*args, entity_type=self.BUSINESS, **kwargs)

    objects = BusinessManager()

    pass


class VirtualTableManager(BaseEntityManager):

    def lookup(self, cache_key, lat, lng, n, count_only=False):
        return super(VirtualTableManager, self).lookup(
            cache_key,
            lat,
            lng,
            n,
            BaseEntity.TABLE,
            count_only
        )

    def users_entities(self, user, include_expired=False):
        if include_expired:
            return user.users_baseentity_related.all().instance_of(VirtualTable)
        else:
            return user.users_baseentity_related.all().instance_of(VirtualTable).exclude(expired=True)

    #AA: TODO : get some max limit on this
    def query_tables(self, name):
        tables = self.filter(Q(tablename__istartswith=name) &
                Q(expired=False)) \
                [0: settings.DEFAULT_MAX_LOOKUP_RESULTS]
        return tables, tables.count()

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
            elif t.is_member(user):
                joined.append(t)
            elif Wizcard.objects.are_wizconnections(
                    user.wizcard,
                    t.creator.wizcard):
                connected.append(t)
            else:
                others.append(t)
        return created, joined, connected, others


class VirtualTable(BaseEntity):
    num_sitting = models.IntegerField(default=0, blank=True)
    password = TruncatingCharField(max_length=40, blank=True)
    # back pointer to any super_entity
    super_entities = RelatedObjectsDescriptor()

    objects = VirtualTableManager()

    def create(self, *args, **kwargs):
        return super(Event, self).create(*args, entity_type=self.TABLE, **kwargs)

    def get_member_wizcards(self):
        members = map(lambda u: u.wizcard, self.users.all().exclude(id=self.creator.id))
        return serialize(members, **fields.wizcard_template_brief)

    def get_creator(self):
        return serialize(self.creator.wizcard, **fields.wizcard_template_brief)

    def table_exchange(self, joinee):
        joined = self.users.all().exclude(id=joinee.id)
        wizcard1 = User.objects.get(id=joinee.pk).wizcard

        wizcards = map(lambda u: u.wizcard, joined)

        for wizcard2 in wizcards:
            cctx = ConnectionContext(asset_obj=self)
            Wizcard.objects.exchange(wizcard1, wizcard2, cctx)

        return self

    def name(self):
        return self.tablename

    def super_entities(self):
        return self.super_entities.related_to()

    def is_member(self, user):
        return bool(self.users.filter(id=user.id).exists())

    def is_creator(self, user):
        return bool(self.creator == user)

    def join_table_and_exchange(self, user, password, skip_password=False):
        #check password
        if (not self.secure) or \
            (self.password == password) or skip_password:
            m, created = UserEntity.user_join(user=user, entity_obj=self)
            if not created:
                #somehow already a member
		        return self
            self.inc_numsitting()

            #send notif to all existing joinees, to update table counts
            for u in self.users.exclude(id=user.id):
                notify.send(
                    user,
                    recipient=u,
                    verb=verbs.WIZCARD_TABLE_JOIN[0],
                    target=self
                )

            self.table_exchange(user)
        else:
            return None
        return self

    def leave_table(self, user):
        try:
            user.membership_set.get(table=self).delete()
            self.dec_numsitting()
        except:
            pass
        #send notif to all members, just like join
        for u in self.users.exclude(id=user.id):
            notify.send(
                user,
                recipient=u,
                verb=verbs.WIZCARD_TABLE_LEAVE[0],
                target=self
            )

        return self

    def delete(self, *args, **kwargs):
        #notify members of deletion (including self)
        verb = kwargs.pop('type', verbs.WIZCARD_TABLE_DESTROY[0])
        members = self.users.all()
        for member in members:
            notify.send(
                self.creator,
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

    def distance_from(self, lat, lng):
        return 0

    def inc_numsitting(self):
        self.num_sitting += 1
        self.save()

    def dec_numsitting(self):
        self.num_sitting -= 1
        self.save()

    def time_remaining(self):
        if not self.expired:
            return self.location.get().timer.get().time_remaining()
        return 0
