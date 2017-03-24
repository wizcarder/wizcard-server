from django.db import models
from taggit.managers import TaggableManager
from media_mgr.models import MediaObjects
from django.contrib.contenttypes import generic
from genericm2m.models import RelatedObjectsDescriptor
from location_mgr.models import LocationMgr
from userprofile.models import UserProfile
from wizcardship.models import Wizcard
from virtual_table.models import VirtualTable
from django.core.exceptions import ObjectDoesNotExist
from location_mgr.signals import location

import pdb

# Create your models here.

class BaseEntity(models.Model):

    class Meta:
        abstract = True

    EVENT = 'EVT'
    BUSINESS = 'BUS'
    PRODUCT = 'PRD'

    ENTITY_CHOICES = (
        (EVENT, 'Event'),
        (BUSINESS, 'Business'),
        (PRODUCT, 'Product'),
    )

    SUB_ENTITY_ENTITY_WIZCARD = 'e_wizcard'
    SUB_ENTITY_ENTITY_TABLE = 'e_table'
    SUB_ENTITY_COMMUNITY_WIZCARD = 'c_wizcard'
    SUB_ENTITY_COMMUNITY_TABLE = 'c_table'

    entity_type = models.CharField(
        max_length=3,
        choices=ENTITY_CHOICES,
        default=EVENT
    )

    created = models.DateTimeField(auto_now_add=True)

    name = models.CharField(max_length=100)
    is_activated = models.BooleanField(default=False)
    address = models.CharField(max_length=80, blank=True)
    website = models.URLField()
    description = models.CharField(max_length=1000)

    # media
    media = generic.GenericRelation(MediaObjects)

    # hashtags.
    tags = TaggableManager()

    owners = models.ManyToManyField(
        UserProfile,
        related_name="owners_%(class)s_related"
    )

    users = models.ManyToManyField(
        UserProfile,
        related_name="users_%(class)s_related"
    )

    # sub-entities. using django-generic-m2m package
    related = RelatedObjectsDescriptor()

    location = generic.GenericRelation(LocationMgr)

    @classmethod
    def get_entity_from_type(self, type):
        from entity.serializers import EventSerializer, ProductSerializer, BusinessSerializer
        if type == self.EVENT:
            cls = Event
            serializer = EventSerializer
        elif type == self.PRODUCT:
            cls = Product
            serializer = ProductSerializer
        elif type == self.BUSINESS:
            cls = Business
            serializer = BusinessSerializer

        return cls, serializer

    def add_subentity_by_id(self, id, type):
        if type == self.SUB_ENTITY_COMMUNITY_WIZCARD or type == self.SUB_ENTITY_ENTITY_WIZCARD:
            try:
                obj = Wizcard.objects.get(id=id)
            except:
                return None
        elif type == self.SUB_ENTITY_ENTITY_TABLE or type == self.SUB_ENTITY_COMMUNITY_TABLE:
            try:
                obj = VirtualTable.objects.get(id=id)
            except:
                return None
        return self.related.connect(obj, alias=type)

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

    def add_user(self, obj):
        self.users.add(obj)

    def remove_owner(self, obj):
        self.users.remove(obj)

    def create_or_update_location(self, lat, lng):
        try:
            l = self.location.get()
            updated = l.do_update(lat, lng)
            # l.reset_timer()
            return updated, l
        except ObjectDoesNotExist:
            updated = False
            # create
            l_tuple = location.send(sender=self, lat=lat, lng=lng,
                                    tree="ETREE")
            #l_tuple[0][1].start_timer(settings.USER_ACTIVE_TIMEOUT)
            return updated, l_tuple[0][1]


class Event(BaseEntity):
    start = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField(auto_now_add=True)


class Product(BaseEntity):
    pass

class Business(BaseEntity):
    pass
