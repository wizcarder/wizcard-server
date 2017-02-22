from django.db import models
from taggit.managers import TaggableManager
from media_mgr.models import MediaObjects
from django.contrib.contenttypes import generic
from genericm2m.models import RelatedObjectsDescriptor
from location_mgr.models import LocationMgr

import pdb

# Create your models here.


class EntityManager(models.Manager):
    pass


class Entity(models.Model):
    EVENT = 'EVT'
    BUSINESS = 'BUS'
    HOSPITAL = 'HOS'
    CLUB = 'CLB'

    tags = TaggableManager()

    ENTITY_CHOICES = (
        (EVENT, 'Event'),
        (BUSINESS, 'Business'),
        (HOSPITAL, 'Hospital'),
        (CLUB, 'Club')
    )

    SUB_ENTITY_ENTITY_WIZCARD = 'e_wizcard'
    SUB_ENTITY_ENTITY_TABLE = 'e_table'
    SUB_ENTITY_COMMUNITY_WIZCARD = 'c_wizcard'
    SUB_ENTITY_COMMUNITY_TABLE = 'c_table'

    created = models.DateTimeField(auto_now_add=True)
    activated = models.BooleanField(default=False)
    entity_type = models.CharField(
        max_length=3,
        choices=ENTITY_CHOICES,
        default=EVENT
    )

    # using django-generic-m2m package
    sub_entities = RelatedObjectsDescriptor()

    location = generic.GenericRelation(LocationMgr)

    # media
    banner = generic.GenericRelation(MediaObjects)
    rolling_media = generic.GenericRelation(MediaObjects)

    def add_sub_entity(self, obj, alias):
        self.sub_entities.connect(obj, alias=alias)

    def get_sub_entities_of_type(self, alias):
        return self.sub_entities.filter(alias=alias).generic_objects()

