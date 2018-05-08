from django.db import models

from django.contrib.auth.models import User

from wizcardship.models import Wizcard
from base.cctx import ConnectionContext
from base_entity.models import BaseEntityComponent, BaseEntity, BaseEntityManager, \
    BaseEntityComponentManager, UserEntity, BaseEntityComponentsOwner
from base_entity.models import EntityEngagementStats
from userprofile.signals import user_type_created
from base.mixins import Base411Mixin, Base412Mixin, PhoneMixin, CompanyTitleMixin, VcardMixin, InviteStateMixin
from taganomy.models import Taganomy
from django.contrib.contenttypes.models import ContentType
from notifications.signals import notify
from wizserver import verbs
import itertools
from django.db.models import Q
import operator


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
        return self.filter(end__lt=timezone.now(), entity_state=BaseEntityComponent.ENTITY_STATE_PUBLISHED)

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

    def update_state_upon_link_unlink(self):
        return True

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

    def get_sub_entities_by_venue(self, type=BaseEntityComponent.SUB_ENTITY_CAMPAIGN):
        sub_entities = self.get_sub_entities_gfk_of_type(alias=type)
        venue_d = {}

        for s in sub_entities:
            if s.object.entity_state != BaseEntityComponent.ENTITY_STATE_DELETED and \
                    'venue' in s.join_fields:
                venue_d.setdefault(s.join_fields['venue'], []).append(s.object.id)

        return venue_d

    # get the invite object associated with this (exhibitor) email recipient
    def get_event_invite(self, email):
        if self.exhibitor_invitees.filter(email=email).exists():
            # should be only 1
            return self.exhibitor_invitees.filter(email=email).get()

        return None

    @property
    def send_wizcard_on_access(self):
        return True

    def user_attach(self, user, state, **kwargs):
        # get PIN out of the way
        if state == UserEntity.PIN:
            return super(Event, self).user_attach(user, state, **kwargs)

        # user_attach can come for non-app users as well. Get that out of the way
        if not user.profile.is_app_user():
            return super(Event, self).user_attach(user, state, **kwargs)

        # now we're left with Join case for App users: Either invited by Organizer or Joined via app.
        do_notify = kwargs.get('do_notify')
        # to track "you have requested access to event" email/push
        info_push_email = False

        # 1: Check if this user is already an attendee attached to Organizer.

        # although unlikely, and should be actively checked for during creation, what if there
        # are multiple matching AttendeeInvitees ? Guess the only way is to do the invite flow
        # for each of them
        atis = AttendeeInvitee.objects.check_existing_attendee_invitees(user, self.get_creator())

        # 2: If so, go through invite flow for secure event or add directly to event for open event
        # we use 2 states. one (state) between user<->event (UserEntity) for the app to keep track
        # and another (invite_state) for the join table between event<->sub-entity. The latter is for portal

        if atis:
            # do 1st pass to gather invite, join_row for each of them.
            join_row_list = []
            for ati in atis:
                # have they been invited to this event already ?
                dont_care, tmp_join_row = ati.check_invite_for_event(self)
                join_row_list.append(tmp_join_row)

            # if atleast one has been already invited, then we will move all invitees to accepted
            atleast_one_invited = any(item for item in join_row_list)

            # do second_pass
            for ati, join_row in itertools.izip(atis, join_row_list):
                if self.secure:
                    # if anyone is invited, we'll do the same for all
                    if atleast_one_invited:
                        invite_state = InviteStateMixin.ACCEPTED
                        if not join_row:
                            # can join him directly. But also relate sub-entity
                            join_row, dont_care = self.add_subentity_obj(
                                ati,
                                BaseEntityComponent.SUB_ENTITY_ATTENDEE_INVITEE
                            )
                    # no one invited yet
                    else:
                        # join user with new state so that app can keep track
                        state = UserEntity.REQUEST_JOIN
                        invite_state = InviteStateMixin.REQUESTED
                        join_row, dont_care = self.add_subentity_obj(
                            ati,
                            BaseEntityComponent.SUB_ENTITY_ATTENDEE_INVITEE
                        )
                        # we won't notify other joinees about this guy until accepted
                        do_notify = False
                        info_push_email = True
                else:
                    invite_state = InviteStateMixin.ACCEPTED
                    if not join_row:
                        join_row, dont_care = self.add_subentity_obj(ati, BaseEntityComponent.SUB_ENTITY_ATTENDEE_INVITEE)

                join_fields = join_row.join_fields
                join_fields.update(invite_state=invite_state)
                join_row.join_fields = join_fields
                join_row.save()
        else:
            atleast_one_invited = False
            # create ATI & attach to Event
            company, title = user.wizcard.get_latest_cc_fields('company', 'title')
            ati = AttendeeInvitee.objects.create(
                entity_type=BaseEntityComponent.ATTENDEE_INVITEE,
                # there is a get_name method in Wizcard, but roundabout here since it picks it up from user model
                name=user.first_name + " " + user.last_name,
                email=user.email,
                company=company,
                title=title,
                phone=user.profile.phone_num_from_username()
            )

            # set the owner
            BaseEntityComponentsOwner.objects.create(
                base_entity_component=ati,
                owner=self.get_creator(),
                is_creator=True
            )

            join_row, dont_care = self.add_subentity_obj(ati, BaseEntityComponent.SUB_ENTITY_ATTENDEE_INVITEE)

            if self.secure:
                invite_state = InviteStateMixin.REQUESTED
                ser = BaseEntityComponent.SERIALIZER_L1
                state = UserEntity.REQUEST_JOIN
                do_notify = False
                info_push_email = True
            else:
                # can join him directly
                invite_state = InviteStateMixin.APP_ACCEPTED
                ser = BaseEntityComponent.SERIALIZER_L2

            join_fields = join_row.join_fields
            join_fields.update(invite_state=invite_state)
            join_row.join_fields = join_fields
            join_row.save()

        kwargs.update(do_notify=do_notify)
        super(Event, self).user_attach(user, state, **kwargs)

        creator = self.get_creator()
        if info_push_email:
            notify.send(
                creator,
                recipient=user,
                notif_tuple=verbs.WIZCARD_INFO,
                target=self,
                action_object=user,
                do_push=True,
                notification_text=verbs.INFO_NOTIFICATION_TEXT[verbs.EVENT_ACCESS_REQUESTED],
                force_sync=True
            )

            notify.send(
                creator,
                recipient=user,
                notif_tuple=verbs.WIZCARD_ENTITY_REQUEST_ATTACH,
                target=self,
                action_object=user,
                do_push=False,
                force_sync=False
            )

            notify.send(
                creator,
                recipient=creator,
                notif_tuple=verbs.WIZCARD_ENTITY_APPROVE_ATTENDEE,
                target=self,
                action_object=creator,
                do_push=False,
                force_sync=False
            )

        if not self.secure:
            ser = BaseEntity.entity_ser_from_type_and_level(
                entity_type=BaseEntityComponent.EVENT,
                level=BaseEntityComponent.SERIALIZER_L2
            )
        elif atleast_one_invited:
            ser = BaseEntity.entity_ser_from_type_and_level(
                entity_type=BaseEntityComponent.EVENT,
                level=BaseEntityComponent.SERIALIZER_L2
            )
        else:
            ser = BaseEntity.entity_ser_from_type_and_level(
                entity_type=BaseEntityComponent.EVENT,
                level=BaseEntityComponent.SERIALIZER_L1
            )

        return ser


class CampaignManager(BaseEntityManager):
    def owners_entities(self, user, entity_type=BaseEntityComponent.CAMPAIGN):
        return super(CampaignManager, self).owners_entities(
            user,
            entity_type=entity_type
        )

    def get_existing_entity(self, name, email, owner):
        # Ideally there should be only 1 campaign for each name, email
        # Also need to normalize name - case insensitive, spaces
        cmp = Campaign.objects.filter(name=name, email=email)
        mycp = [cp for cp in cmp if cp.is_owner(owner)]
        return mycp[0] if mycp else None

    def users_entities(self, user, user_filter={}, entity_filter={}):
        entity_filter.update(entity_type=BaseEntityComponent.CAMPAIGN)
        return super(CampaignManager, self).users_entities(user, user_filter=user_filter, entity_filter=entity_filter)

    def combine_search(self, query, entity_type=BaseEntityComponent.CAMPAIGN):
        return super(CampaignManager, self).combine_search(query, entity_type=entity_type)


class Campaign(BaseEntity):
    # when this is set, it'll show on the landing screen
    is_sponsored = models.BooleanField(default=False)

    objects = CampaignManager()

    def update_state_upon_link_unlink(self):
        return True

    def post_connect_remove(self, parent, **kwargs):
        # don't send notif here if is parent is not event.
        if parent.entity_type != BaseEntityComponent.EVENT:
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

    # no notifs required for this one
    def post_connect_remove(self, parent, **kwargs):
        kwargs.update(send_notif=False)
        return super(CoOwners, self).post_connect_remove(parent, **kwargs)


class AttendeeInviteeManager(BaseEntityComponentManager):
    def owners_entities(self, user, entity_type=BaseEntityComponent.ATTENDEE_INVITEE):
        return super(AttendeeInviteeManager, self).owners_entities(
            user,
            entity_type=entity_type
        )

    # see if any attendee_invitees exist for the organizer that match this app_user
    def check_existing_attendee_invitees(self, app_user, organizer_user):
        qs = self.owners_entities(organizer_user, entity_type=BaseEntityComponent.ATTENDEE_INVITEE)

        # 1. check with phone number
        phone = app_user.profile.phone_num_from_username()
        email = app_user.email

        qs = self.all().exclude(entity_state=BaseEntityComponent.ENTITY_STATE_DELETED)

        qlist = list()

        qlist.append(Q(phone=phone))
        qlist.append(Q(email=email.lower()))

        return qs.filter(reduce(operator.or_, qlist)).distinct()

class AttendeeInvitee(BaseEntityComponent, Base411Mixin, PhoneMixin, CompanyTitleMixin):
    objects = AttendeeInviteeManager()

    # check if any app_users match this attendee_invitee
    # returns Tuple (True/False, [list of matches of type User])
    def check_existing_app_users(self):
        from userprofile.models import AppUser, UserProfile
        qs = AppUser.objects.all()

        qlist = list()
        if self.phone:
            username = UserProfile.objects.username_from_phone_num(self.phone)
            qlist.append(Q(profile__user__username=username))
        if self.email:
            qlist.append(Q(profile__user__email=self.email))

        if qlist:
            res = qs.filter(reduce(operator.or_, qlist)).distinct()
            return bool(res), res

        return False, AppUser.objects.none()

    def check_invite_for_event(self, event):
        return event.has_join_table_row(self), event.get_join_table_row(self)

    # no notifs required for this one
    def post_connect_remove(self, parent, **kwargs):
        kwargs.update(send_notif=False)
        return super(AttendeeInvitee, self).post_connect_remove(parent, **kwargs)


class ExhibitorInviteeManager(BaseEntityComponentManager):
    def owners_entities(self, user, entity_type=BaseEntityComponent.EXHIBITOR_INVITEE):
        return super(ExhibitorInviteeManager, self).owners_entities(
            user,
            entity_type=entity_type
        )

    def check_pending_invites(self, email):
        return self.filter(email=email, invite_state=ExhibitorInvitee.INVITED)


class ExhibitorInvitee(BaseEntityComponent, Base411Mixin, InviteStateMixin):
    exhibitor = models.ForeignKey(Campaign, null=True, blank=True, default=None, related_name='exhibitor_invitees')
    event = models.ForeignKey(Event, related_name='exhibitor_invitees')

    objects = ExhibitorInviteeManager()

    # no notifs required for this one
    def post_connect_remove(self, parent, **kwargs):
        kwargs.update(send_notif=False)
        return super(ExhibitorInvitee, self).post_connect_remove(parent, **kwargs)


class AgendaManager(BaseEntityComponentManager):
    def owners_entities(self, user, entity_type=BaseEntityComponent.AGENDA):
        return super(AgendaManager, self).owners_entities(
            user,
            entity_type=entity_type
        )


class Agenda(BaseEntityComponent, Base412Mixin):
    objects = AgendaManager()

    def update_state_upon_link_unlink(self):
        return True

    def delete(self, *args, **kwargs):
        type = kwargs.get('type', BaseEntityComponent.ENTITY_DELETE)

        for item in self.items.all():
            item.delete(*args, **kwargs)

        super(Agenda, self).delete(*args, **kwargs)


class AgendaItem(BaseEntity):
    agenda_key = models.ForeignKey(Agenda, related_name='items')
    start = models.DateTimeField(default=timezone.now)
    end = models.DateTimeField(default=timezone.now)
    where = models.CharField(max_length=100, blank=True)

    # override method to skip immediate parent and get agenda's parent
    def get_parent_entities(self, **kwargs):
        return self.agenda_key.get_parent_entities(**kwargs)

    def delete(self, *args, **kwargs):
        # clear related join table
        self.related.all().delete()

        # have to trigger notif from here since this is not coming via
        # the add_remove_subentity path
        BaseEntityComponent.objects.notify_via_entity_parent(
            self,
            verbs.WIZCARD_ENTITY_DELETE,
            verbs.NOTIF_OPERATION_DELETE
        )

        super(AgendaItem, self).delete(*args, **kwargs)


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

