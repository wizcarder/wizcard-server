__author__ = 'aammundi'

from django.db import models
from base.char_trunc import TruncatingCharField
from base.emailField import EmailField
from picklefield.fields import PickledObjectField

class Base411Mixin(models.Model):
    class Meta:
        abstract = True

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    name = TruncatingCharField(max_length=20, default="")
    email = EmailField(blank=True)

class Base412Mixin(Base411Mixin):
    class Meta:
        abstract = True

    website = models.URLField(blank=True)
    description = models.CharField(max_length=1000, blank=True)
    ext_fields = PickledObjectField(default={}, blank=True)


class Base413Mixin(Base412Mixin):
    class Meta:
        abstract = True

    phone = TruncatingCharField(max_length=20, blank=True)


class Base414Mixin(Base413Mixin):
    class Meta:
        abstract = True

    address = models.CharField(max_length=80, blank=True)



