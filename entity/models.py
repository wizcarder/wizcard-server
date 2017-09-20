from django.db import models

from django.contrib.auth.models import User

from wizcardship.models import Wizcard
from lib.preserialize.serialize import serialize
from wizserver import verbs
from base.cctx import ConnectionContext
from base_entity.models import BaseEntityComponent, BaseEntityComponentManager, BaseEntity, BaseEntityManager
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

    def users_entities(self, user, entity_type=BaseEntity.EVENT, include_expired=False):
        return super(EventManager, self).users_entities(
            user,
            entity_type=entity_type,
            include_expired=include_expired
        )

    def expire(self):
        evts = self.filter(end__lt=timezone.now(), expired=False)
        evids = []
        for e in evts:
            e.expire_and_notif()
            evids.append(str(e.id))
        return evids

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

    def notify_update(self):
        self.notify_all_users(
            self,
            verbs.WIZCARD_EVENT_UPDATE[0],
            self,
            exclude_sender=False,
            filter_users=True
        )

    def notify_delete(self):
        self.notify_all_users(
            self,
            verbs.WIZCARD_EVENT_DELETE[0],
            self
        )

    def expire_and_notif(self, flag=True):
        self.expired = flag
        self.save()
        self.notify_expire()

    def notify_expire(self):
        self.notify_all_users(
            self,
            verbs.WIZCARD_EVENT_EXPIRE[0],
            self
        )


class ProductManager(BaseEntityManager):
    def users_entities(self, user, entity_type=BaseEntity.PRODUCT, include_expired=False):
        return super(ProductManager, self).users_entities(
            user,
            entity_type=entity_type,
            include_expired=include_expired
        )


class Product(BaseEntity):

    objects = ProductManager()

    # this is a follow
    def join(self, user):
        super(Product, self).join(user)

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
        super(Product, self).leave(user)

        # send notif to all members, just like join
        self.notify_all_users(
            user,
            verbs.WIZCARD_ENTITY_LEAVE[0],
            self,
        )

        return


class BusinessManager(BaseEntityManager):
    def users_entities(self, user, entity_type=BaseEntity.BUSINESS, include_expired=False):
        return super(BusinessManager, self).users_entities(
            user,
            entity_type=entity_type,
            include_expired=include_expired
        )

class Business(BaseEntity):

    objects = BusinessManager()

    pass


class VirtualTableManager(BaseEntityManager):
    def users_entities(self, user, entity_type=BaseEntity.TABLE, include_expired=False):
        return super(VirtualTableManager, self).users_entities(
            user,
            entity_type=entity_type,
            include_expired=include_expired
        )

    def lookup(self, lat, lng, n, etype=BaseEntity.TABLE, count_only=False):
        return super(VirtualTableManager, self).lookup(
            lat,
            lng,
            n,
            etype,
            count_only
        )

    def serialize(self, tables, template):
        return serialize(tables, **template)

    def serialize_split(self, tables, user, template):
        created, joined, connected, others = self.split_table(tables, user)

        s = dict()
        if created:
            s['created'] = self.serialize(created, template)
        if joined:
            s['joined'] = self.serialize(joined, template)
        if connected:
            s['connected'] = self.serialize(connected, template)
        if others:
            s['others'] = self.serialize(others, template)
        return s

    def split_table(self, tables, user):
        created = []
        joined = []
        connected = []
        others = []
        for t in tables:
            if t.is_creator(user):
                created.append(t)
            elif t.is_joined(user):
                joined.append(t)
            elif Wizcard.objects.are_wizconnections(
                    user.wizcard,
                    t.get_creator().wizcard):
                connected.append(t)
            else:
                others.append(t)
        return created, joined, connected, others


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

class AgendaManager(BaseEntityComponentManager):

    def users_agenda(self, user):
        return super(SpeakerManager, self).users_components(user, Speaker)

class Agenda(BaseEntityComponent):

    objects = AgendaManager()

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


from django.dispatch import receiver
from django.db.models.signals import post_save

@receiver(post_save, sender=Event)
@receiver(post_save, sender=Product)
@receiver(post_save, sender=Business)
@receiver(post_save, sender=VirtualTable)
def create_engagement_stats(sender, instance, created, **kwargs):
    if created:
        e = EntityEngagementStats.objects.create()
        instance.engagements = e
        instance.save()




#from entity.models import BaseEntityComponent



