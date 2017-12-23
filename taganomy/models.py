from django.db import models

# Create your models here.
from django.db import models
from taggit.managers import TaggableManager
from base_entity.models import BaseEntityComponent, BaseEntityComponentManager
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import User



import pdb

# Create your models here.

# Its a Taxanomy + tags => Taganomy

class TaganomyManager(BaseEntityComponentManager):

    def get_category(self, tags):
        cats = self.filter(tags__name__in=[tags])
        return cats

    def get_default_category(self):
        from userprofile.models import UserProfile
        return Taganomy.objects.get(
            category=Taganomy.CATEGORY_OTHERS,
            editor=UserProfile.objects.get_admin_user()
        )

class Taganomy(BaseEntityComponent):

    category = models.CharField(max_length=100)
    tags = TaggableManager()


    objects = TaganomyManager()

    def add_tags(self, tags):
        self.tags.add(*tags)

    def remove_tags(self, tags):
        self.tags.remove(*tags)

    def get_tags(self):
        return self.tags.names()

