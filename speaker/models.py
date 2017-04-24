# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from base.emailField import EmailField
import pdb

# Create your models here.

#This should be called a Panelist (for ease of understanding and current requirements calling it speaker)



class Speaker(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100)
    is_activated = models.BooleanField(default=False)
    #SPeaker need not be a user in our system
    user = models.ForeignKey(User, null=True, default=None)
    social_profile = models.URLField(default=None)
    email = EmailField(blank=True)
    thumbnail = models.URLField(default=None)
    org = models.CharField(max_length=100, default=None)
    designation = models.CharField(max_length=100, default=None)
    description = models.TextField(default="Not Available")





