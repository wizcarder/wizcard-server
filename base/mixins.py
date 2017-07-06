__author__ = 'aammundi'

from django.db import models
from base.char_trunc import TruncatingCharField
from base.emailField import EmailField
from picklefield.fields import PickledObjectField


class Base411_Mixin(models.Model):
    class Meta:
        abstract = True

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    address = models.CharField(max_length=80, blank=True)
    website = models.URLField(blank=True)
    description = models.CharField(max_length=1000, blank=True)
    phone = TruncatingCharField(max_length=20, blank=True)
    email = EmailField(blank=True)
    ext_fields = PickledObjectField(default={}, blank=True)


