from django.db import models

from django.contrib.auth.models import User

from wizcardship.models import Wizcard
from wizserver import verbs
from base.cctx import ConnectionContext
from base_entity.models import BaseEntityComponent, BaseEntity, BaseEntityManager, BaseEntityComponentManager
from base_entity.models import EntityEngagementStats
from userprofile.signals import user_type_created
from notifications.signals import notify
from base.mixins import Base411Mixin, Base412Mixin, CompanyTitleMixin, VcardMixin, InviteStateMixin
import pdb




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
        kwargs.update(entity_type=BaseEntityComponent.EVENT)
        return super(EventManager, self).users_entities(
            user,
            **kwargs
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
            verbs.WIZCARD_ENTITY_UPDATE,
            self
        )

    def get_tagged_entities(self, tag, entity_type=BaseEntityComponent.SUB_ENTITY_CAMPAIGN):
        sub_entities = self.get_sub_entities_id_of_type(entity_type)
        # TODO: AR: Get sub entities with a particular tag
        '''
        taganomy = self.get_subentity_of_type(entity_type=BaseEntityComponent.SUB_ENTITY_CATEGORY)[0]
        
        tagged_entities = taganomy.get_entities(tags__in=tag)
        '''



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
            **kwargs
        )


class Campaign(BaseEntity):

    objects = CampaignManager()

    def notify_update(self):
        self.notify_all_users(
            self.get_creator(),
            verbs.WIZCARD_ENTITY_UPDATE,
            self
        )


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
            **kwargs
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

class Sponsor(BaseEntity, InviteStateMixin):
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


class AttendeeInvitee(BaseEntityComponent, Base411Mixin, InviteStateMixin):
    objects = AttendeeInviteeManager()


class ExhibitorInviteeManager(BaseEntityComponentManager):
    def owners_entities(self, user, entity_type=BaseEntityComponent.EXHIBITOR_INVITEE):
        return super(ExhibitorInviteeManager, self).owners_entities(
            user,
            entity_type=entity_type
        )

    # check if invitee_ids is in User based on email.
    # returns those users
    def check_existing_users_exhibitors(self, invitee_ids):
        matched_users = User.objects.filter(
            email__in=self.filter(
                id__in=invitee_ids
            ).values_list('email', flat=True)
        )

        matched_exhibitors = self.filter(
            email__in=matched_users.values_list('email', flat=True)
        )

        return matched_users, matched_exhibitors

    def check_pending_invites(self, email):
        return self.filter(email=email, state=ExhibitorInvitee.INVITED)

class ExhibitorInvitee(BaseEntityComponent, Base411Mixin, InviteStateMixin):

    objects = ExhibitorInviteeManager()

class AgendaManager(BaseEntityComponentManager):
    def owners_entities(self, user, entity_type=BaseEntityComponent.AGENDA):
        return super(AgendaManager, self).owners_entities(
            user,
            entity_type=entity_type
        )


class Agenda(BaseEntityComponent):
    objects = AgendaManager()


class AgendaItem(BaseEntity):
    agenda = models.ForeignKey(Agenda, related_name='items')
    start = models.DateTimeField(default=timezone.now)
    end = models.DateTimeField(default=timezone.now)


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

@receiver(user_type_created)
def connect_subentities(sender, **kwargs):
    b_usr = sender.get_baseuser_by_type(kwargs.pop('user_type'))
    b_usr.connect_subentities()
