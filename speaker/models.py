# Create your models here.

from django.db import models
from taggit.managers import TaggableManager
from django.contrib.contenttypes import generic
from userprofile.models import UserProfile
from django.core.exceptions import ObjectDoesNotExist
from base.char_trunc import TruncatingCharField
from base.emailField import EmailField
from django.contrib.contenttypes.models import ContentType


import pdb

# Create your models here.

#This should be called a Panelist (for ease of understanding and current requirements calling it speaker)



class Speaker(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100)
    is_activated = models.BooleanField(default=False)
    #SPeaker need not be a user in our system
    userprofile = models.ForeignKey(UserProfile, null=True, default=None)
    social_profile = models.URLField(default=None)
    email = EmailField(blank=True)
    thumbnail = models.URLField(default=None)
    org = models.CharField(max_length=100, default=None)
    designation = models.CharField(max_length=100, default=None)
    description = models.TextField(default="Not Available")





