from django.conf import settings
from django.db import models
from django.contrib.contenttypes import generic
from media_mgr.models import MediaObjects
from base.mixins import Base411Mixin, Base412Mixin, Base413Mixin, CompanyTitleMixin, \
    VcardMixin
from userprofile.models import WebOrganizerUser

# Create your models here.


class Speaker(Base412Mixin, CompanyTitleMixin, VcardMixin):
    user = models.OneToOneField(WebOrganizerUser)
    media = generic.GenericRelation(MediaObjects)


class Sponsor(Base413Mixin):
    user = models.OneToOneField(WebOrganizerUser)
    media = generic.GenericRelation(MediaObjects)
    caption = models.CharField(max_length=50, default='Not Available')


class CoOwners(Base411Mixin):
    user = models.OneToOneField(WebOrganizerUser)
    is_creator = models.BooleanField(default=False)


class AttendeeInvitee(Base411Mixin):
    user = models.OneToOneField(WebOrganizerUser)
