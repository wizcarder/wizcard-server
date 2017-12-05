from django.db import models

from django.contrib.auth.models import User

from wizcardship.models import Wizcard
from lib.preserialize.serialize import serialize
from wizserver import verbs
from base.cctx import ConnectionContext
from base_entity.models import BaseEntityComponent, BaseEntity, BaseEntityManager, BaseEntityComponentManager
from base_entity.models import EntityEngagementStats


from notifications.signals import notify
from base.mixins import Base411Mixin, Base412Mixin, Base413Mixin, CompanyTitleMixin, \
    VcardMixin

from django.utils import timezone
now = timezone.now

# Create your models here.

class EventManager(BaseEntityManager):
    def lookup(self, lat, lng, n, etype=BaseEntityComponent.EVENT, count_only=False):
        return super(EventManager, self).lookup(
            lat,
            lng,
            n,
            etype,
            count_only
        )

    def owners_entities(self, user, entity_type=BaseEntityComponent.EVENT):
        return super(EventManager, self).owners_entities(
            user,
            entity_type=entity_type
        )

    def users_entities(self, user, **kwargs):
        return super(EventManager, self).users_entities(
            user,
            kwargs
        )

    def get_expired(self):
        return self.filter(end__lt=timezone.now(), expired=False, is_activated=True)


class Event(BaseEntity):
    start = models.DateTimeField(default=timezone.now)
    end = models.DateTimeField(default=timezone.now)

    objects = EventManager()

    def notify_update(self):
        self.notify_all_users(
            self.get_creator(),
            verbs.WIZCARD_ENTITY_UPDATE[0],
            self
        )


class CampaignManager(BaseEntityManager):
    def owners_entities(self, user, entity_type=BaseEntityComponent.CAMPAIGN):
        return super(CampaignManager, self).owners_entities(
            user,
            entity_type=entity_type
        )

    def users_entities(self, user, **kwargs):
        kwargs.update(entity_type=BaseEntityComponent.CAMPAIGN)
        return super(CampaignManager, self).users_entities(
            user,
            kwargs
        )


class Campaign(BaseEntity):

    objects = CampaignManager()


class VirtualTableManager(BaseEntityManager):
    def owners_entities(self, user, entity_type=BaseEntityComponent.TABLE):
        return super(VirtualTableManager, self).owners_entities(
            user,
            entity_type=entity_type
        )

    def users_entities(self, user, **kwargs):
        kwargs.update(entity_type=BaseEntityComponent.TABLE)
        return super(VirtualTableManager, self).users_entities(
            user,
            kwargs
        )

    def lookup(self, lat, lng, n, etype=BaseEntityComponent.TABLE, count_only=False):
        return super(VirtualTableManager, self).lookup(
            lat,
            lng,
            n,
            etype,
            count_only
        )


class VirtualTable(BaseEntity):

    objects = VirtualTableManager()

    def table_exchange(self, joinee):
        joined = self.users.all().exclude(id=joinee.id)
        wizcard1 = User.objects.get(id=joinee.pk).wizcard

        wizcards = map(lambda u: u.wizcard, joined)

        for wizcard2 in wizcards:
            cctx = ConnectionContext(asset_obj=self)
            Wizcard.objects.exchange(wizcard1, wizcard2, cctx)

        return self

    def delete(self, *args, **kwargs):
        # notify members of deletion (including self)
        verb = kwargs.pop('type', verbs.WIZCARD_TABLE_DESTROY[0])
        members = self.users.all()
        for member in members:
            notify.send(self.get_creator(),
                        recipient=member,
                        notif_type=verb,
                        target=self
                        )

        self.location.get().delete()

        if verb == verbs.WIZCARD_TABLE_TIMEOUT[0]:
            self.expired = True
            self.save()
        else:
            self.users.clear()
            super(VirtualTable, self).delete(*args, **kwargs)

    def time_remaining(self):
        if not self.expired:
            return self.location.get().timer.get().time_remaining()
        return 0


class SpeakerManager(BaseEntityComponentManager):
    def owners_entities(self, user, entity_type=BaseEntityComponent.SPEAKER):
        return super(SpeakerManager, self).owners_entities(
            user,
            entity_type=entity_type
        )


class Speaker(BaseEntityComponent, Base412Mixin, CompanyTitleMixin, VcardMixin):
    objects = SpeakerManager()


class SponsorManager(BaseEntityManager):
    def owners_entities(self, user, entity_type=BaseEntityComponent.SPONSOR):
        return super(SponsorManager, self).owners_entities(
            user,
            entity_type=entity_type
        )

    def users_entities(self, user, **kwargs):
        kwargs.update(entity_type=BaseEntityComponent.SPONSOR)
        return super(SponsorManager, self).users_entities(
            user,
            **kwargs
        )

class Sponsor(BaseEntity):
    caption = models.CharField(max_length=50, default='Not Available')

    objects = SponsorManager()


class CoOwnersManager(BaseEntityComponentManager):
    def owners_entities(self, user, entity_type=BaseEntityComponent.COOWNER):
        return super(CoOwnersManager, self).owners_entities(
            user,
            entity_type=entity_type
        )


class CoOwners(BaseEntityComponent):
    # the user model for this guy
    user = models.OneToOneField(User)

    objects = CoOwnersManager()


class AttendeeInviteeManager(BaseEntityComponentManager):
    def owners_entities(self, user, entity_type=BaseEntityComponent.ATTENDEE_INVITEE):
        return super(AttendeeInviteeManager, self).owners_entities(
            user,
            entity_type=entity_type
        )


class AttendeeInvitee(BaseEntityComponent, Base411Mixin):
    objects = AttendeeInviteeManager()


class ExhibitorInviteeManager(BaseEntityComponentManager):
    def owners_entities(self, user, entity_type=BaseEntityComponent.EXHIBITOR_INVITEE):
        return super(ExhibitorInviteeManager, self).owners_entities(
            user,
            entity_type=entity_type
        )


class ExhibitorInvitee(BaseEntityComponent, Base411Mixin):

    objects = ExhibitorInviteeManager()

    @classmethod
    def validate(cls, exhibitors):
        failed_ids = ""
        valid_emails = []
        for eid in exhibitors:
            try:
                email = ExhibitorInvitee.objects.get(id=eid).email
                valid_emails.append(email)
            except:
                failed_ids = failed_ids + "," + str(eid)
        return valid_emails, failed_ids


class AgendaManager(BaseEntityComponentManager):
    def owners_entities(self, user, entity_type=BaseEntityComponent.AGENDA):
        return super(AgendaManager, self).owners_entities(
            user,
            entity_type=entity_type
        )


class Agenda(BaseEntityComponent):
    objects = AgendaManager()


class AgendaItem(BaseEntityComponent, Base412Mixin):
    agenda = models.ForeignKey(Agenda, related_name='items')
    start = models.DateTimeField(default=timezone.now)
    end = models.DateTimeField(default=timezone.now)
    where = models.CharField(max_length=100, default="")


from django.dispatch import receiver
from django.db.models.signals import post_save


@receiver(post_save, sender=Event)
@receiver(post_save, sender=Campaign)
@receiver(post_save, sender=Sponsor)
@receiver(post_save, sender=VirtualTable)
def create_engagement_stats(sender, instance, created, **kwargs):
    if created:
        e = EntityEngagementStats.objects.create()
        instance.engagements = e
        instance.save()
