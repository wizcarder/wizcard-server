from django.db import models

from django.contrib.auth.models import User

from wizcardship.models import Wizcard
from lib.preserialize.serialize import serialize
from wizserver import verbs
from base.cctx import ConnectionContext
from base_entity.models import BaseEntityComponent, BaseEntity, BaseEntityManager, BaseEntityComponentManager
from base_entity.models import EntityEngagementStats, UserEntity


from notifications.signals import notify
from base.mixins import Base411Mixin, Base412Mixin, Base413Mixin, CompanyTitleMixin, \
    VcardMixin

from django.utils import timezone
now = timezone.now

# Create your models here.

class EventManager(BaseEntityManager):
    def lookup(self, lat, lng, n, etype=BaseEntity.EVENT, count_only=False):
        return super(EventManager, self).lookup(
            lat,
            lng,
            n,
            etype,
            count_only
        )

    def owners_entities(self, user, entity_type=BaseEntity.EVENT):
        return super(EventManager, self).owners_entities(
            user,
            entity_type=entity_type
        )

    def users_entities(self, user, entity_type=BaseEntity.EVENT):
        return super(EventManager, self).users_entities(
            user,
            entity_type=entity_type
        )

class Event(BaseEntity):
    start = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField(auto_now_add=True)

    objects = EventManager()

    def join(self, user):
        super(Event, self).join(user)

        self.notify_all_users(
            user,
            verbs.WIZCARD_ENTITY_JOIN[0],
            self,
        )
        # do any event specific stuff here
        return

    def leave(self, user):
        super(Event, self).leave(user)

        self.notify_all_users(
            user,
            verbs.WIZCARD_ENTITY_LEAVE[0],
            self,
        )

        return


class CampaignManager(BaseEntityManager):
    def owners_entities(self, user, entity_type=BaseEntity.CAMPAIGN):
        return super(CampaignManager, self).owners_entities(
            user,
            entity_type=entity_type
        )

    def users_entities(self, user, entity_type=BaseEntity.CAMPAIGN):
        return super(CampaignManager, self).users_entities(
            user,
            entity_type=entity_type
        )


class Campaign(BaseEntity):

    objects = CampaignManager()

    # this is a follow
    def join(self, user):
        super(Campaign, self).join(user)

        self.notify_all_users(
            user,
            verbs.WIZCARD_ENTITY_JOIN[0],
            self,
        )

        return

    # this is an un-follow. Will happen when product is either
    # deleted from rolodex or if there is a button on the campaign
    # to un-follow
    def leave(self, user):
        super(Campaign, self).leave(user)

        # send notif to all members, just like join
        self.notify_all_users(
            user,
            verbs.WIZCARD_ENTITY_LEAVE[0],
            self,
        )

        return


class VirtualTableManager(BaseEntityManager):
    def owners_entities(self, user, entity_type=BaseEntity.TABLE):
        return super(VirtualTableManager, self).owners_entities(
            user,
            entity_type=entity_type
        )

    def users_entities(self, user, entity_type=BaseEntity.TABLE):
        return super(VirtualTableManager, self).users_entities(
            user,
            entity_type=entity_type
        )

    def lookup(self, lat, lng, n, etype=BaseEntity.TABLE, count_only=False):
        return super(VirtualTableManager, self).lookup(
            lat,
            lng,
            n,
            etype,
            count_only
        )


class VirtualTable(BaseEntity):

    objects = VirtualTableManager()

    def join(self, user):
        super(VirtualTable, self).join(user)

        self.notify_all_users(
            user,
            verbs.WIZCARD_ENTITY_JOIN[0],
            self,
        )
        return

    def leave(self, user):
        super(VirtualTable, self).leave(user)

        self.notify_all_users(
            user,
            verbs.WIZCARD_ENTITY_LEAVE[0],
            self,
        )
        return

    def table_exchange(self, joinee):
        joined = self.users.all().exclude(id=joinee.id)
        wizcard1 = User.objects.get(id=joinee.pk).wizcard

        wizcards = map(lambda u: u.wizcard, joined)

        for wizcard2 in wizcards:
            cctx = ConnectionContext(asset_obj=self)
            Wizcard.objects.exchange(wizcard1, wizcard2, cctx)

        return self

    def delete(self, *args, **kwargs):
        #notify members of deletion (including self)
        verb = kwargs.pop('type', verbs.WIZCARD_TABLE_DESTROY[0])
        members = self.users.all()
        for member in members:
            notify.send(
                self.get_creator(),
                recipient=member,
                verb=verb,
                target=self)

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
    def owners_entities(self, user, entity_type=BaseEntity.SPEAKER):
        return super(SpeakerManager, self).owners_entities(
            user,
            entity_type=entity_type
        )


class Speaker(BaseEntityComponent, Base412Mixin, CompanyTitleMixin, VcardMixin):
    objects = SpeakerManager()


class SponsorManager(BaseEntityComponentManager):
    def owners_entities(self, user, entity_type=BaseEntity.SPONSOR):
        return super(SponsorManager, self).owners_entities(
            user,
            entity_type=entity_type
        )


class Sponsor(BaseEntityComponent, Base413Mixin):
    caption = models.CharField(max_length=50, default='Not Available')

    objects = SponsorManager()


class CoOwnersManager(BaseEntityComponentManager):
    def owners_entities(self, user, entity_type=BaseEntity.COOWNER):
        return super(CoOwnersManager, self).owners_entities(
            user,
            entity_type=entity_type
        )

class CoOwners(BaseEntityComponent, Base411Mixin):
    objects = CoOwnersManager()


class AttendeeInviteeManager(BaseEntityComponentManager):
    def owners_entities(self, user, entity_type=BaseEntity.ATTENDEE_INVITEE):
        return super(AttendeeInviteeManager, self).owners_entities(
            user,
            entity_type=entity_type
        )


class AttendeeInvitee(BaseEntityComponent, Base411Mixin):
    objects = AttendeeInviteeManager()


class ExhibitorInviteeManager(BaseEntityComponentManager):
    def owners_entities(self, user, entity_type=BaseEntity.EXHIBITOR_INVITEE):
        return super(ExhibitorInviteeManager, self).owners_entities(
            user,
            entity_type=entity_type
        )


class ExhibitorInvitee(BaseEntityComponent, Base411Mixin):
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


class Agenda(BaseEntityComponent):
    start = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField(auto_now_add=True)
    where = models.CharField(max_length=100, default="")


from django.dispatch import receiver
from django.db.models.signals import post_save

@receiver(post_save, sender=Event)
@receiver(post_save, sender=Campaign)
@receiver(post_save, sender=VirtualTable)
def create_engagement_stats(sender, instance, created, **kwargs):
    if created:
        e = EntityEngagementStats.objects.create()
        instance.engagements = e
        instance.save()




#from entity.models import BaseEntityComponent



