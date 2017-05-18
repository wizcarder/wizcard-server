from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from media_mgr.signals import media_create
import pdb

# Create your models here.

class MediaObjectsManager(models.Manager):

    def get_media_of_type(self, type):
        return MediaObjects.objects.filter(media_type=type)

    def get_media_of_subtype(self, subtype):
        return MediaObjects.objects.filter(media_sub_type=subtype)


class MediaObjects(models.Model):

    objects = MediaObjectsManager

    def __repr__(self):
        return str(self.id) + "." + self.media_type + "." + self.media_sub_type

    TYPE_IMAGE = 'IMG'
    TYPE_VIDEO = 'VID'

    SUB_TYPE_BANNER = 'BNR'
    SUB_TYPE_LOGO = 'LGO'
    SUB_TYPE_SPONSORS_LOGO = 'SLG'
    SUB_TYPE_ROLLING = 'ROL'
    SUB_TYPE_THUMBNAIL = 'THB'

    MEDIA_CHOICES = (
        (TYPE_IMAGE, 'Image'),
        (TYPE_VIDEO, 'Video'),
    )

    MEDIA_SUBTYPE_CHOICES = (
        (SUB_TYPE_BANNER, 'Banner'),
        (SUB_TYPE_LOGO, 'Logo'),
        (SUB_TYPE_SPONSORS_LOGO, 'Sponsor Logo'),
        (SUB_TYPE_ROLLING, 'Rolling'),
        (SUB_TYPE_THUMBNAIL, 'Thumbnail')
    )

    media_type = models.CharField(
        max_length=3,
        choices=MEDIA_CHOICES,
        default=TYPE_IMAGE
    )

    media_sub_type = models.CharField(
        max_length=3,
        choices=MEDIA_SUBTYPE_CHOICES,
        default=SUB_TYPE_ROLLING
    )

    # url of media element
    media_element = models.URLField(blank=True, default=None)
    media_iframe = models.URLField(blank=True)

    # GenericForeignKey to objects requiring media objects
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')


def media_create_handler(**kwargs):
    sender = kwargs.pop('sender')
    objs = kwargs.pop('objs', None)

    if objs:
        mobjs = [MediaObjects(
            object_id=sender.pk,
            content_type=ContentType.objects.get_for_model(sender),
            **obj) for obj in objs]
        MediaObjects.objects.bulk_create(mobjs)

media_create.connect(media_create_handler, dispatch_uid='media_mgr.models.media_objects')
