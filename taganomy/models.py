from django.db import models

# Create your models here.
from django.db import models
from taggit.managers import TaggableManager
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import User



import pdb

# Create your models here.

# Its a Taxanomy + tags => Taganomy

class TaganomyManager(models.Manager):

    def get_category(self, tags):
        cats = self.filter(tags__name__in=[tags])
        return cats

    def get_default_category(self):
        from userprofile.models import UserProfile
        return Taganomy.objects.get(
            category=Taganomy.CATEGORY_OTHERS,
            editor=UserProfile.objects.get_admin_user()
        )

class Taganomy(models.Model):

    CATEGORY_OTHERS = "Others"

    category = models.CharField(max_length=100)
    tags = TaggableManager()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    editor = models.ForeignKey(User)

    objects = TaganomyManager()

    def add_tags(self, tags, editwho):
        self.tags.add(tags)
        self.editor = editwho

    def remove_tags(self, tags, editwho):
        self.tags.remove(tags)
        self.editor = editwho

    def get_tags(self):
        return self.tags.names()

