
from django.db import models
from base.mixins import Base411Mixin, Base412Mixin, Base413Mixin, CompanyTitleMixin, \
    VcardMixin, MediaMixin
from entity.models import BaseEntityComponent, BaseEntityComponentManager


# Create your models here


class MediaEntitiesManager(BaseEntityComponentManager):

    def users_media(self, user):
        umedia = user.owners_baseentitycomponent_related.all().instance_of(MediaEntities)
        return umedia


class MediaEntities(BaseEntityComponent, MediaMixin):

    objects = MediaEntitiesManager()


class SpeakerManager(BaseEntityComponentManager):

    def users_speakers(self, user):
        return super(SpeakerManager, self).users_components(user, Speaker)


class Speaker(BaseEntityComponent, Base412Mixin, CompanyTitleMixin, VcardMixin):

    objects = SpeakerManager()


class SponsorManager(BaseEntityComponentManager):
    def users_sponsors(self, user):
        return super(SponsorManager, self).users_components(user, Sponsor)


class Sponsor(BaseEntityComponent, Base413Mixin):
    caption = models.CharField(max_length=50, default='Not Available')

    objects = SponsorManager()


class CoOwners(BaseEntityComponent, Base411Mixin):
    pass


class AttendeeInvitee(BaseEntityComponent, Base411Mixin):
    pass

class ExhibitorInvitee(BaseEntityComponent, Base411Mixin):
    pass