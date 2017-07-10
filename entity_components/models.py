from django.conf import settings
from django.db import models
from django.contrib.contenttypes import generic
from media_mgr.models import MediaObjects
from base.mixins import Base411Mixin, Base412Mixin, Base413Mixin, CompanyTitleMixin, \
    VcardMixin
from entity.models import BaseEntityComponent


# Create your models here

class Speaker(BaseEntityComponent, Base412Mixin, CompanyTitleMixin, VcardMixin):
    media = generic.GenericRelation(MediaObjects)


class Sponsor(BaseEntityComponent, Base413Mixin):
    media = generic.GenericRelation(MediaObjects)
    caption = models.CharField(max_length=50, default='Not Available')


class CoOwner(BaseEntityComponent, Base411Mixin):
    pass


class AttendeeInvitee(BaseEntityComponent, Base411Mixin):
    pass


class ExhibitorInvitee(BaseEntityComponent, Base411Mixin):
    pass