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

    def get_tagged_entities(self, tags, entity_type):
        return super(TaganomyManager, self).get_tagged_entities(tags, entity_type)


class Taganomy(BaseEntityComponent, Base411Mixin):

    objects = TaganomyManager()

    def delete_related_tags(self, tags):
        related = self.related.all().generic_objects()
        remove_tags = Tag.objects.filter(id__in=tags)
        map(lambda x: x.tags.remove(*remove_tags), related)

    def register_object(self, obj):
        self.add_subentity_obj(obj, BaseEntityComponent.sub_entity_type_from_entity_type(obj.entity_type))

    def get_sub_entities_by_tags(self, entity_type=BaseEntityComponent.SUB_ENTITY_CAMPAIGN):
        sub_entities = self.get_sub_entities_of_type(entity_type)
        tag_d = {}
        for s in sub_entities:
            tags = s.tags.all()
            for t in tags:
                tag_d.setdefault(t.name, []).append(s.id)

        return tag_d

    # not sending tag level notif. Only at Taganomy level
    def post_connect_remove(self, parent, **kwargs):
        kwargs.update(send_notif=False)
        return super(Taganomy, self).post_connect_remove(parent, **kwargs)

    def is_floodable(self):
        return True

    def flood_set(self, **kwargs):
        flood_list = []
        # this will be the flood_set of it's parent entities. Assumption is that only 1-parent entity
        parent = self.get_parent_entities(exclude=[self.ENTITY_STATE_DELETED, self.ENTITY_STATE_EXPIRED]).pop()
        if not parent:
            return flood_list

        return parent.flood_set(**kwargs)


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
