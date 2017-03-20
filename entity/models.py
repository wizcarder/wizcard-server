from django.db import models
from taggit.managers import TaggableManager
from media_mgr.models import MediaObjects
from django.contrib.contenttypes import generic
from genericm2m.models import RelatedObjectsDescriptor
from location_mgr.models import LocationMgr
from userprofile.models import UserProfile
from wizcardship.models import Wizcard
from virtual_table.models import VirtualTable

import pdb

# Create your models here.


class BaseEntityManager(models.Manager):
    def get_entity_from_type(self, type):
        if type == BaseEntity.EVENT:
            cls = Event
        elif type == BaseEntity.PRODUCT:
            cls = Product
        elif type == BaseEntity.BUSINESS:
            cls = Business

        return cls


class BaseEntity(models.Model):

    class Meta:
        abstract = True

    objects = BaseEntityManager()

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

    owners = models.ManyToManyField(UserProfile)

    # sub-entities. using django-generic-m2m package
    related = RelatedObjectsDescriptor()

    location = generic.GenericRelation(LocationMgr)

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

    def remove_owner(self, obj):
        self.owners.remove(obj)


class Event(BaseEntity):
    start = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField(auto_now_add=True)


class Product(BaseEntity):
    pass

class Business(BaseEntity):
    pass
