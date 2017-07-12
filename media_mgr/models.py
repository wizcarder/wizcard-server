from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from media_mgr.signals import media_create
from base.mixins import MediaMixin

from django.utils import timezone

now = timezone.now

import pdb

# Create your models here.


class MediaObjectsQuerySet(models.QuerySet):
    def delete(self):
        # TODO: delete s3 assets
        super(MediaObjectsQuerySet, self).delete()


class MediaObjects(MediaMixin):
    def __repr__(self):
        return str(self.id) + "." + str(self.media_type) + "." + str(self.media_sub_type)


    # GenericForeignKey to objects requiring media objects
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    objects = MediaObjectsQuerySet.as_manager()

    def upload_s3(self, b64image):
        raw_image = b64image.decode('base64')
        upfile = SimpleUploadedFile("%s-%s.jpg" % \
                                        (self.media_sub_type, now().strftime("%Y-%m-%d %H:%M")),
                                        raw_image, "image/jpeg")
        self.upload_file.save(upfile.name, upfile)
        self.media_element = self.upload_file.remote_url()

        return self.upload_file.local_path(), self.upload_file.remote_url()


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
