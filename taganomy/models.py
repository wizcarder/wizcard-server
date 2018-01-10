from django.db import models

# Create your models here.
from django.db import models
from base_entity.models import BaseEntityComponent, BaseEntityComponentManager
from django.db.models.signals import m2m_changed
from django.contrib.contenttypes.models import ContentType
from taggit.models import Tag
from base.mixins import Base411Mixin

import pdb

# Create your models here.

# Its a Taxanomy + tags => Taganomy


class TaganomyManager(BaseEntityComponentManager):

    def owners_entities(self, user, entity_type=BaseEntityComponent.CATEGORY):
        return super(TaganomyManager, self).owners_entities(
            user,
            entity_type=entity_type
        )

    def get_category(self, tags):
        cats = self.filter(tags__name__in=[tags])
        return cats




class Taganomy(BaseEntityComponent, Base411Mixin):


    objects = TaganomyManager()

    def delete_related_tags(self, tags):
        related = self.related.all().generic_objects()
        remove_tags = Tag.objects.filter(id__in=tags)
        map(lambda x: x.tags.remove(*remove_tags), related)

    def register_object(self, obj):
        self.add_subentity_obj(obj, obj.entity_type)



def tag_signal_handler(sender, **kwargs):

    instance = kwargs.pop("instance", None)
    action = kwargs.pop("action", None)
    tag_ids = kwargs.pop("pk_set", [None])

    if action == "post_remove" and \
            ContentType.objects.get_for_model(instance) == ContentType.objects.get(model="taganomy"):
        instance.delete_related_tags(list(tag_ids))
    else:
        return


m2m_changed.connect(tag_signal_handler, sender=Taganomy.tags.through)
