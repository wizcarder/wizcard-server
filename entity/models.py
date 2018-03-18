from django.db import models

from django.contrib.auth.models import User

from wizcardship.models import Wizcard
from base.cctx import ConnectionContext
from base_entity.models import BaseEntityComponent, BaseEntity, BaseEntityManager, \
    BaseEntityComponentManager
from base_entity.models import EntityEngagementStats
from userprofile.signals import user_type_created
from base.mixins import Base411Mixin, Base412Mixin, CompanyTitleMixin, VcardMixin, InviteStateMixin
from taganomy.models import Taganomy
from django.contrib.contenttypes.models import ContentType

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

    def users_entities(self, user, user_filter={}, entity_filter={}):
        entity_filter.update(entity_type=BaseEntityComponent.EVENT)

        return super(EventManager, self).users_entities(user, user_filter, entity_filter)

    def get_expired(self):
        return self.filter(end__lt=timezone.now(), entity_state=BaseEntityComponent.ENTITY_STATE_EXPIRED)

    def get_tagged_entities(self, tags, entity_type):
        events = Event.objects.filter(entity_state=BaseEntityComponent.ENTITY_STATE_PUBLISHED)
        t_events = []

        taganomy = Taganomy.objects.get_tagged_entities(tags, BaseEntityComponent.CATEGORY)
        contenttype_id = ContentType.objects.get(model="event")

        for t_obj in taganomy:
            t_events = t_events + t_obj.get_parent_entities_by_contenttype_id(contenttype_id)

        return list(set(events) & set(t_events))

    def combine_search(self, query, entity_type=BaseEntityComponent.EVENT):
        return super(EventManager, self).combine_search(query, entity_type)


class Event(BaseEntity):
    start = models.DateTimeField(default=timezone.now)
    end = models.DateTimeField(default=timezone.now)

    objects = EventManager()

    def get_parent_entities(self, **kwargs):
        # no parent for event
        return [self]

    def delete(self, *args, **kwargs):
        type = kwargs.get('type', BaseEntityComponent.ENTITY_DELETE)

        if type == BaseEntityComponent.ENTITY_EXPIRE:
            for subent in self.related.all().generic_objects():
                subent.delete(*args, **kwargs)
        else:
            self.related.all().delete()

        super(Event, self).delete(*args, **kwargs)


class CampaignManager(BaseEntityManager):
    def owners_entities(self, user, entity_type=BaseEntityComponent.CAMPAIGN):
        return super(CampaignManager, self).owners_entities(
            user,
            entity_type=entity_type
        )

    def users_entities(self, user, user_filter={}, entity_filter={}):
        entity_filter.update(entity_type=BaseEntityComponent.CAMPAIGN)
        return super(CampaignManager, self).users_entities(user, user_filter=user_filter, entity_filter=entity_filter)

    def combine_search(self, query, entity_type=BaseEntityComponent.CAMPAIGN):
        return super(CampaignManager, self).combine_search(query, entity_type=entity_type)


class Campaign(BaseEntity):
    # when this is set, it'll show on the landing screen
    is_sponsored = models.BooleanField(default=False)

    objects = CampaignManager()

    def post_connect_remove(self, parent, **kwargs):
        # don't send notif here if is parent is Taganomy.
        if parent.entity_type == BaseEntityComponent.CATEGORY:
            kwargs.update(send_notif=False)

        return super(Campaign, self).post_connect_remove(parent, **kwargs)


class VirtualTableManager(BaseEntityManager):
    def owners_entities(self, user, entity_type=BaseEntityComponent.TABLE):
        return super(VirtualTableManager, self).owners_entities(
            user,
            entity_type=entity_type
        )

    def users_entities(self, user, user_filter={}, entity_filter={}):
        entity_filter.update(entity_type=BaseEntityComponent.TABLE)
        return super(VirtualTableManager, self).users_entities(
            user,
            user_filter=user_filter,
            entity_filter=entity_filter
        )

    def lookup(self, lat, lng, n, etype=BaseEntityComponent.TABLE, count_only=False):
        return super(VirtualTableManager, self).lookup(
            lat,
            lng,
            n,
            etype,
            count_only
        )

    def combine_search(self, query, entity_type=BaseEntityComponent.TABLE):
        return super(VirtualTableManager, self).combine_search(query, entity_type=entity_type)


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

    def time_remaining(self):
        if not self.is_expired():
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

    def users_entities(self, user, user_filter={}, entity_filter={}):
        entity_filter.update(entity_type=BaseEntityComponent.SPONSOR)
        return super(SponsorManager, self).users_entities(user, user_filter=user_filter, entity_filter=entity_filter)


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

    # no notifs required for this one
    def post_connect(self, parent, **kwargs):
        kwargs.update(send_notif=False)
        return super(CoOwners, self).post_connect(parent, **kwargs)


class AttendeeInviteeManager(BaseEntityComponentManager):
    def owners_entities(self, user, entity_type=BaseEntityComponent.ATTENDEE_INVITEE):
        return super(AttendeeInviteeManager, self).owners_entities(
            user,
            entity_type=entity_type
        )

    def check_existing_users_attendees(self, invitee_ids):
        matched_users = User.objects.filter(
            email__in=self.filter(
                id__in=invitee_ids
            ).values_list('email', flat=True)
        )

        matched_attendees = self.filter(
            email__in=matched_users.values_list('email', flat=True)
        )

        return matched_users, matched_attendees


class AttendeeInvitee(BaseEntityComponent, Base411Mixin, CompanyTitleMixin, InviteStateMixin):
    objects = AttendeeInviteeManager()

    # no notifs required for this one
    def post_connect(self, parent, **kwargs):
        kwargs.update(send_notif=False)
        return super(AttendeeInvitee, self).post_connect(parent, **kwargs)


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

    # no notifs required for this one
    def post_connect(self, parent, **kwargs):
        kwargs.update(send_notif=False)
        return super(ExhibitorInvitee, self).post_connect(parent, **kwargs)


class AgendaManager(BaseEntityComponentManager):
    def owners_entities(self, user, entity_type=BaseEntityComponent.AGENDA):
        return super(AgendaManager, self).owners_entities(
            user,
            entity_type=entity_type
        )


class Agenda(BaseEntityComponent, Base412Mixin):
    objects = AgendaManager()

    def delete(self, *args, **kwargs):
        type = kwargs.get('type', BaseEntityComponent.ENTITY_DELETE)

        for item in self.items.all():
            item.delete(*args, **kwargs)

        super(Agenda, self).delete(*args, **kwargs)


class AgendaItem(BaseEntity):
    agenda_key = models.ForeignKey(Agenda, related_name='items')
    start = models.DateTimeField(default=timezone.now)
    end = models.DateTimeField(default=timezone.now)

    # override method to skip immediate parent and get agenda's parent
    def get_parent_entities(self, **kwargs):
        return self.agenda_key.get_parent_entities(**kwargs)


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
    # AA: Review. What happens when multiple user_types exist for User
    b_usr = sender.get_baseuser_by_type(kwargs.pop('user_type'))
    b_usr.connect_subentities()

