from django.db import models
from base.char_trunc import TruncatingCharField
from base.emailField import EmailField
from picklefield.fields import PickledObjectField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from base.custom_storage import WizcardQueuedS3BotoStorage
from base.custom_field import WizcardQueuedFileField
import os


def get_s3_bucket(instance, filename):
    if instance.media_sub_type == MediaMixin.SUB_TYPE_F_BIZCARD:
        folder = "bizcards"
    elif instance.media_sub_type == MediaMixin.SUB_TYPE_THUMBNAIL:
        folder = "thumbnails"
    else:
        folder = "deadcards"

    return os.path.join(folder, filename)


class VcardMixin(models.Model):
    class Meta:
        abstract = True

    vcard = models.TextField(blank=True)


class CompanyTitleMixin(models.Model):
    class Meta:
        abstract = True

    company = TruncatingCharField(max_length=40, blank=True)
    title = TruncatingCharField(max_length=200, blank=True)


class Base411Mixin(models.Model):
    class Meta:
        abstract = True

    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    name = TruncatingCharField(max_length=50, default="")
    email = EmailField(blank=True)


class Base412Mixin(Base411Mixin):
    class Meta:
        abstract = True

    website = models.URLField(blank=True)
    description = models.CharField(max_length=1000, blank=True)
    ext_fields = PickledObjectField(default={}, blank=True)


class Base413Mixin(Base412Mixin, VcardMixin):
    class Meta:
        abstract = True

    phone = TruncatingCharField(max_length=20, blank=True)


class Base414Mixin(Base413Mixin):
    class Meta:
        abstract = True

    address = models.CharField(max_length=200, blank=True)


class OwnersRelationshipMixin(models.Model):
    class Meta:
        abstract = True

    # gfk to owner. (assuming it can be OrganizerUser, ExhibitorUser)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def add_owner(self, obj):
        self. content_type = ContentType.objects.get_for_model(obj)
        self.object_id = obj.pk


class MediaMixin(models.Model):
    class Meta:
        abstract = True

    TYPE_IMAGE = 'IMG'
    TYPE_VIDEO = 'VID'
    TYPE_DOC = 'DOC'

    SUB_TYPE_BANNER = 'BNR'
    SUB_TYPE_LOGO = 'LGO'
    SUB_TYPE_SPONSORS_LOGO = 'SLG'
    SUB_TYPE_ROLLING = 'ROL'
    SUB_TYPE_THUMBNAIL = 'THB'
    SUB_TYPE_F_BIZCARD = 'FBZ'
    SUB_TYPE_D_BIZCARD = 'DBZ'
    SUB_TYPE_PROFILE_VIDEO = 'PVD'
    SUB_TYPE_AGENDA = 'AGN'

    MEDIA_CHOICES = (
        (TYPE_IMAGE, 'Image'),
        (TYPE_VIDEO, 'Video'),
        (TYPE_DOC, 'Doc')
    )

    MEDIA_SUBTYPE_CHOICES = (
        (SUB_TYPE_BANNER, 'Banner'),
        (SUB_TYPE_LOGO, 'Logo'),
        (SUB_TYPE_SPONSORS_LOGO, 'Sponsor Logo'),
        (SUB_TYPE_ROLLING, 'Rolling'),
        (SUB_TYPE_THUMBNAIL, 'Thumbnail'),
        (SUB_TYPE_F_BIZCARD, 'Business Card Front'),
        (SUB_TYPE_D_BIZCARD, 'Dead Business Card'),
        (SUB_TYPE_PROFILE_VIDEO, 'Profile Video'),
        (SUB_TYPE_AGENDA, 'Agenda')
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
