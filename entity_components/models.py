from django.conf import settings
from django.db import models
from django.contrib.contenttypes import generic
from media_mgr.models import MediaObjects
from base.mixins import Base411Mixin, Base412Mixin, Base413Mixin
from base.char_trunc import TruncatingCharField

# Create your models here.

class EventComponentMixin(models.Model):
    caption = models.CharField(max_length=50, default='Not Available')
    media = generic.GenericRelation(MediaObjects)

    class Meta:
        abstract = True

class Speaker(EventComponentMixin, Base412Mixin):
    vcard = models.TextField(blank=True)
    org = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)

class SpeakerEvent(models.Model):
    speaker = models.ForeignKey(Speaker)
    event = models.ForeignKey('entity.Event')
    description = models.CharField(max_length=1000)

class Sponsor(EventComponentMixin, Base413Mixin):
    class Meta:
        pass


class SponsorEvent(models.Model):
    sponsor = models.ForeignKey(Sponsor)
    event = models.ForeignKey('entity.Event')
    campaign = models.ForeignKey('entity.Product', null=True, blank=True)

    def add_campaign(self, campaign):
        self.campaign = campaign
        self.save()


class TeamOwner(Base411Mixin):
    class Meta:
        pass

class AttendeeInvitee(Base411Mixin):
    class Meta:
        pass