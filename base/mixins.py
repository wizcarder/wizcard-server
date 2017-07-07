__author__ = 'aammundi'

from django.db import models
from base.char_trunc import TruncatingCharField
from base.emailField import EmailField
from picklefield.fields import PickledObjectField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class VcardMixin(models.Model):
    class Meta:
        abstract = True

    vcard = models.TextField(blank=True)


class CompanyTitleMixin(models.Model):
    class Meta:
        abstract = True

    company = TruncatingCharField(max_length=40, blank=True)
    title = TruncatingCharField(max_length=200, blank=True)


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


class Base413Mixin(Base412Mixin, VcardMixin):
    class Meta:
        abstract = True

    phone = TruncatingCharField(max_length=20, blank=True)


class Base414Mixin(Base413Mixin):
    class Meta:
        abstract = True

    address = models.CharField(max_length=80, blank=True)


class OwnersRelationshipMixin(models.Model):
    class Meta:
        abstract = True

    # gfk to owner. (assuming it can be OrganizerUser, ExhibitorUser)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def add_owner(self, obj):
        self. content_type = ContentType.objects.get_for_model(obj)
        self.object_id = obj.pk



