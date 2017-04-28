# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from base.emailField import EmailField
import pdb

# Create your models here.


class Speaker(User):
    social_profile = models.URLField(default=None)
    thumbnail = models.URLField(default=None)
    org = models.CharField(max_length=100, default=None)
    designation = models.CharField(max_length=100, default=None)
    description = models.TextField(default="Not Available")