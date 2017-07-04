from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from media_mgr.signals import media_create
from base.custom_storage import WizcardQueuedS3BotoStorage
from base.custom_field import WizcardQueuedFileField
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

now = timezone.now

import pdb

# Create your models here.

def get_s3_bucket(instance, filename):
    if instance.media_sub_type == MediaObjects.SUB_TYPE_F_BIZCARD:
        return "deadcards"
    elif instance.media_sub_type == MediaObjects.SUB_TYPE_THUMBNAIL:
        return "thumbnails"
    else:
        return "bizcards"

class MediaObjectsQuerySet(models.QuerySet):
    def delete(self):
        # TODO: delete s3 assets
        super(MediaObjectsQuerySet, self).delete()


class MediaObjects(models.Model):
    def __repr__(self):
        return str(self.id) + "." + str(self.media_type) + "." + str(self.media_sub_type)

    TYPE_IMAGE = 'IMG'
    TYPE_VIDEO = 'VID'

    SUB_TYPE_BANNER = 'BNR'
    SUB_TYPE_LOGO = 'LGO'
    SUB_TYPE_SPONSORS_LOGO = 'SLG'
    SUB_TYPE_ROLLING = 'ROL'
    SUB_TYPE_THUMBNAIL = 'THB'
    SUB_TYPE_F_BIZCARD = 'FBZ'
    SUB_TYPE_D_BIZCARD = 'DBZ'
    SUB_TYPE_PROFILE_VIDEO = 'PVD'

    MEDIA_CHOICES = (
        (TYPE_IMAGE, 'Image'),
        (TYPE_VIDEO, 'Video'),
    )

    MEDIA_SUBTYPE_CHOICES = (
        (SUB_TYPE_BANNER, 'Banner'),
        (SUB_TYPE_LOGO, 'Logo'),
        (SUB_TYPE_SPONSORS_LOGO, 'Sponsor Logo'),
        (SUB_TYPE_ROLLING, 'Rolling'),
        (SUB_TYPE_THUMBNAIL, 'Thumbnail'),
        (SUB_TYPE_F_BIZCARD, 'Business Card Front'),
        (SUB_TYPE_D_BIZCARD, 'Dead Business Card'),
        (SUB_TYPE_PROFILE_VIDEO, 'Profile Video')
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
    # s3 upload file field. Used for scanned cards
    upload_file = WizcardQueuedFileField(
        storage=WizcardQueuedS3BotoStorage(delayed=False),
        upload_to=get_s3_bucket,
        blank=True
    )

    # url of media element
    media_element = models.URLField(blank=True, default=None)
    media_iframe = models.URLField(blank=True)

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
