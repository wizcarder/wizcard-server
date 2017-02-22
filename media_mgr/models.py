from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

# Create your models here.

class MediaObjects(models.Model):

    IMAGE = 'IMG'
    VIDEO = 'VID'

    MEDIA_CHOICES = (
        (IMAGE, 'Image'),
        (VIDEO, 'Video'),
    )

    media_type = models.CharField(
        max_length=3,
        choices=MEDIA_CHOICES,
        default=IMAGE
    )

    # url of media element
    media_element = models.URLField(blank=True, default=None)
    media_iframe = models.URLField(blank=True)

    # GenericForeignKey to objects requiring media objects
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
