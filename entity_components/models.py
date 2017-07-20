
from django.db import models

#from entity.models import BaseEntityComponent, BaseEntityComponentManager
from django.core.files.uploadedfile import SimpleUploadedFile
from entity_components.signals import media_create
from django.utils import timezone
from base.mixins import MediaMixin
from entity.models import BaseEntityComponent, BaseEntityComponentManager
import pdb
from django.contrib.contenttypes.models import ContentType

now = timezone.now


# Create your models here

class MediaEntitiesQuerySet(models.QuerySet):
    def delete(self):
        # TODO: use this to delete s3 assets for app part
        super(MediaEntitiesQuerySet, self).delete()

    def users_media(self, user):
        umedia = user.owners_baseentitycomponent_related.all().instance_of(MediaEntities)
        return umedia


class MediaEntities(BaseEntityComponent, MediaMixin):
    def __repr__(self):
        return str(self.id) + "." + str(self.media_type) + "." + str(self.media_sub_type)

    objects = MediaEntitiesQuerySet.as_manager()

    def upload_s3(self, b64image):
        raw_image = b64image.decode('base64')
        upfile = SimpleUploadedFile("%s-%s.jpg" % (self.media_sub_type, now().strftime("%Y-%m-%d %H:%M")),
                                    raw_image, "image/jpeg")
        self.upload_file.save(upfile.name, upfile)
        self.media_element = self.upload_file.remote_url()

        return self.upload_file.local_path(), self.upload_file.remote_url()

    def related_connect(self, owner_obj):
        owner_obj.connect(self, alias=ContentType.objects.get_for_model(self).name)


def media_create_handler(**kwargs):
    # this will be User object
    sender = kwargs.pop('sender')
    objs = kwargs.pop('objs', [])

    e = [BaseEntityComponent.create(MediaEntities, owner=sender, is_creator=True, **mobjs) for mobjs in objs]

    # note, related is not handled by this.
    return e


media_create.connect(media_create_handler, dispatch_uid='entity_components.models.media_entities')

