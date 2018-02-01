"""
.. autoclass:: WizConnectionRequest
    :members:

.. autoclass:: WizcardManager
    :members:

.. autoclass:: Wizcard
    :members:

.. autoclass:: UserBlocks
    :members:
"""


from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
import signals
import pdb
from django.contrib.contenttypes import generic
from location_mgr.signals import location
from location_mgr.models import LocationMgr
from base.char_trunc import TruncatingCharField
from base.mixins import Base413Mixin
from picklefield.fields import PickledObjectField
from django.conf import settings
import logging
import operator
from django.db.models import Q
from lib import wizlib
from wizcard import err
from wizserver import verbs
from notifications.signals import notify
from notifications.models import SyncNotification
from django.db.models import URLField
from polymorphic.models import PolymorphicModel
from polymorphic.manager import PolymorphicManager
from base.mixins import MediaMixin
from lib.ocr import OCR
from base.mixins import CompanyTitleMixin
from genericm2m.models import RelatedObjectsDescriptor
from notifications.models import BaseNotification

logger = logging.getLogger(__name__)


class WizcardManager(PolymorphicManager):
    def except_wizcard(self, except_user):
        qs = Wizcard.objects.filter(~Q(user=except_user))
        return qs

    #is 2 following 1..ie, does 2 have 1's card
    def is_wizcard_following(self, wizcard1, wizcard2):
        return bool(wizcard1.wizconnections_to.filter(requests_to__status=verbs.ACCEPTED, id=wizcard2.id).exists())

    #is req from 1 to 2, pending
    def is_wizconnection_pending(self, wizcard1, wizcard2):
        return bool(wizcard1.wizconnections_to.filter(requests_to__status=verbs.PENDING, id=wizcard2.id).exists())

    #has wizcard1 sent a req to wizcard2
    def is_wizconnection(self, wizcard1, wizcard2):
        return bool(wizcard1.wizconnections_to.filter(id=wizcard2.id).exists())

    #2-way check
    def are_wizconnections(self, wizcard1, wizcard2):
        return self.is_wizcard_following(wizcard1, wizcard2) and \
               self.is_wizcard_following(wizcard2, wizcard1)

    #wizcard1 sends req to wizcard2
    def cardit(self, wizcard1, wizcard2, status=verbs.PENDING, cctx=""):
        return wizcard1.add_relationship(wizcard2, status=status, ctx=cctx)

    #wizcard1 withdraws previously sent relationship
    def uncardit(self, wizcard1, wizcard2, soft=True):
        if soft:
            wizcard1.set_delete_relationship(wizcard2)
        else:
            wizcard1.remove_relationship(wizcard2)

    #wizcard2 follows wizcard1 (accepts wizcard1's req)
    def becard(self, wizcard1, wizcard2, cctx=""):
        rel = wizcard1.get_relationship(wizcard2)
        if cctx:
            rel.cctx = cctx
        rel.accept()
        return rel

    #decline request wizcard1->wizcard2
    def uncard(self, wizcard1, wizcard2):
        rel = wizcard1.get_relationship(wizcard2)
        rel.decline()
        return rel

    #reset the relationship wizcard1->wizcard2 back to pending
    def reset(self, wizcard1, wizcard2):
        rel = wizcard1.get_relationship(wizcard2)
        rel.reset()

    #wrapper for 2-way exchanges
    def exchange(self, wizcard1, wizcard2, cctx):
        if self.are_wizconnections(wizcard1, wizcard2):
            return  err.EXISTING_CONNECTION

        #setup bidir relationships
        rel1 = Wizcard.objects.cardit(wizcard1, wizcard2, status=verbs.ACCEPTED, cctx=cctx)
        rel2 = Wizcard.objects.cardit(wizcard2, wizcard1, status=verbs.ACCEPTED, cctx=cctx)

        #send Type 1 notification to both
        notify.send(
            wizcard1.user, recipient=wizcard2.user,
            notif_tuple=verbs.WIZREQ_T,
            description=cctx.description,
            target=wizcard1,
            action_object=rel1,
            delivery_type=BaseNotification.DELIVERY_TYPE_SYNC
        )

        notify.send(
            wizcard2.user, recipient=wizcard1.user,
            description=cctx.description,
            target=wizcard2,
            notif_tuple=verbs.WIZREQ_T,
            action_object=rel2,
            delivery_type=BaseNotification.DELIVERY_TYPE_SYNC
        )

        return err.OK

    def update_wizconnection(self, wizcard1, wizcard2, half=False):
        notify.send(
            wizcard1.user,
            recipient=wizcard2.user,
            notif_tuple=verbs.WIZCARD_UPDATE_HALF if half else verbs.WIZCARD_UPDATE,
            target=wizcard1,
            delivery_type=BaseNotification.DELIVERY_TYPE_SYNC
        )

    def query_users(self, exclude_user, name, phone, email):
        #name can be first name, last name or even combined
        #any of the arguments may be null
        qlist = []

        if name:
            split = name.split()
            for n in split:
                name_result = (Q(user__first_name__istartswith=n) | Q(user__last_name__istartswith=n))
                qlist.append(name_result)

        #phone
        if phone:
            phone_result = (Q(phone=phone) | Q(phone2__startswith=phone))
            qlist.append(phone_result)

        #email
        if email:
            email_result = Q(email=email.lower())
            qlist.append(email_result)

        result = self.filter(reduce(operator.or_, qlist)).exclude(user_id=exclude_user.id).\
            exclude(user__profile__baseuser__appuser__settings__is_visible=False)

        return result, len(result)

    def get_admin_wizcard(self):
        return User.objects.filter(is_staff=True, is_superuser=True)[0] \
            if User.objects.filter(is_staff=True, is_superuser=True).exists() else None

    def get_connection_status(self, wizcard1, wizcard2):
        if wizcard2.is_admin_wizcard():
            return verbs.ADMIN
        if wizcard1 == wizcard2:
            return verbs.OWN
        elif Wizcard.objects.are_wizconnections(wizcard1, wizcard2):
            return verbs.CONNECTED
        elif Wizcard.objects.is_wizcard_following(wizcard1, wizcard2):
            # other guy is a follower
            # split into 2 cases here. if the reverse relationship is in pending, then
            # follower, else follower-d (reverse connection was either deleted or declined)
            if Wizcard.objects.is_wizconnection_pending(wizcard2, wizcard1):
                return verbs.FOLLOWER
            else:
                return verbs.FOLLOWER_D
        elif Wizcard.objects.is_wizcard_following(wizcard2, wizcard1):
            # I'm following him
            return verbs.FOLLOWED
        else:
            return verbs.OTHERS

    def friends_in_wizcards(self, my_wizcard, wizcards):
        return [x for x in wizcards if Wizcard.objects.is_wizcard_following(x, my_wizcard)]

class WizcardBase(PolymorphicModel, Base413Mixin):
    sms_url = URLField(blank=True)
    media = RelatedObjectsDescriptor()

    def get_latest_company(self):
        qs = self.contact_container.all()
        if qs.exists():
            return qs[0].company
        return None

    def is_admin_wizcard(self):
        return self.user.profile.is_admin

    def save_sms_url(self,url):
        self.sms_url = wizlib.shorten_url(url)
        self.save()

    def get_sms_url(self):
        return self.sms_url

    def get_thumbnail_url(self):
        l = [x.media_element for x in self.media.all().generic_objects() if x.media_sub_type == MediaMixin.SUB_TYPE_THUMBNAIL]
        if l:
            return l

        return ""

    def save_vcard(self, vobj):
        self.vcard = vobj
        self.save()

    def get_name(self):
        return self.user.first_name + " " + self.user.last_name

    def get_video_url(self):
        l = [(x.media_element, x.media_iframe) for x in self.media.all().generic_objects() if x.media_type==MediaMixin.TYPE_VIDEO]
        if l:
            return l

        return ""

    @property
    def get_ext_fields(self):
        return self.ext_fields

    @property
    def get_vcard(self):
        return self.vcard

    @property
    def get_email(self):
        return self.email

    def get_latest_title(self):
        qs = self.contact_container.all()
        if qs.exists():
            return qs[0].title
        return None


class Wizcard(WizcardBase):
    # TODO move this upstairs
    user = models.OneToOneField(User, related_name='wizcard')

    wizconnections_to = models.ManyToManyField('self',
                                            through='WizConnectionRequest',
                                            symmetrical=False,
                                            related_name='wizconnections_from')

    media = RelatedObjectsDescriptor()

    objects = WizcardManager()

    class Meta:
        verbose_name = _(u'wizcard')
        verbose_name_plural = _(u'wizcards')

    def __unicode__(self):
        return _(u'%(user)s\'s wizcard') % {'user': unicode(self.user)}

    def wizconnection_count(self):
        return self.get_connections().count()

    wizconnection_count.short_description = _(u'Cards count')

    def wizconnection_summary(self, count=7):
        wizconnection_list = self.get_connections().all().select_related()[:count]
        return u'[%s%s]' % (u', '.join(unicode(f.user) for f in wizconnection_list),
                            u', ...' if self.wizconnection_count() > count else u'')

    wizconnection_summary.short_description = _(u'Summary of wizconnections')

    def serialize_wizconnections(self):
        out = []
        # doing import here to avoid circular import. This does affect performance
        # (eventhough django caches re-imports). Still, doing it here since this
        # method is called only in the resync path
        from wizcardship.serializers import WizcardSerializerL1, WizcardSerializerL2
        admin = self.get_admin_wizcard()
        out.append(WizcardSerializerL2(admin, many=True, context={'status': verbs.ADMIN}).data)

        connected = self.get_connections_without_admin()
        if connected:
            out.append(WizcardSerializerL2(connected, many=True, context={'status': verbs.CONNECTED}).data)

        following = self.get_following_only()
        if following:
            out.append(WizcardSerializerL1(following, many=True, context={'status': verbs.FOLLOWED}).data)

        return out

    def flood(self):
        # full card for connections and half for followers
        for wizcard in self.get_connections():
            Wizcard.objects.update_wizconnection(self, wizcard, half=False)

        for wizcard in self.get_followers_only():
            Wizcard.objects.update_wizconnection(self, wizcard, half=True)

    def check_flick_duplicates(self, lat, lng):
        if not settings.DO_FLICK_AGGLOMERATE:
            return None
        #check if nearby cards can be combined...do we need to adjust centroid and all that ?
        for w in self.flicked_cards.exclude(expired=True):
            if wizlib.haversine(w.lng, w.lat, lng, lat) < settings.WIZCARD_FLICK_AGGLOMERATE_RADIUS:
                return w
        return None

    def get_relationship(self, wizcard):
        try:
            return WizConnectionRequest.objects.get(
                        from_wizcard=self,
                        to_wizcard=wizcard)
        except:
            return None

    def add_relationship(self, wizcard, status=verbs.PENDING, ctx=""):
        rel = self.get_relationship(wizcard)
        if not rel:
            rel = WizConnectionRequest.objects.create(
                from_wizcard=self,
                to_wizcard=wizcard,
                cctx=ctx,
                status=status)
        else:
            rel.cctx=ctx
            rel.status=status
            rel.save()
        return rel

    def remove_relationship(self, wizcard):
        WizConnectionRequest.objects.filter(
            from_wizcard=self,
            to_wizcard=wizcard).delete()

    def set_delete_relationship(self, wizcard):
        WizConnectionRequest.objects.filter(
            from_wizcard=self,
            to_wizcard=wizcard).update(status=verbs.DELETED)

    # ME ->
    def get_connected_to(self, status):
        return self.wizconnections_to.filter(
            requests_to__status=status)

    # ME <-
    def get_connected_from(self, status):
        return self.wizconnections_from.filter(
            requests_from__status=status)

    # cards I have deleted
    def get_deleted(self):
        return self.wizconnections_from.filter(
            requests_from__status=verbs.DELETED
        )

    #2 way connected...
    def get_connections(self):
        return self.wizconnections_to.filter(
            requests_to__status=verbs.ACCEPTED,
            requests_from__status=verbs.ACCEPTED,
            requests_from__to_wizcard=self
        )

    #2 way connected + admin wizcard
    def get_connections_without_admin(self):
        return self.wizconnections_to.filter(
            Q(user__profile__is_admin=False) |
            Q(requests_to__status=verbs.ACCEPTED,
              requests_from__status=verbs.ACCEPTED,
              requests_from__to_wizcard=self
              )
        ).distinct()

    def get_admin_wizcard(self):
        # ofcourse, optimal way is to simply look up via UserProfile, or
        # even cache the admin wizcard. importing UserProfile here is causing
        # circular import issue
        return self.wizconnections_to.filter(Q(user__profile__is_admin=True))

    def get_pending_from(self):
        return self.get_connected_from(verbs.PENDING)

    # those having my card (=my flood list)
    # wrapper around get_connected_to
    def get_followers(self):
        return self.get_connected_to(verbs.ACCEPTED)

    #my rolodex
    def get_following(self):
        return self.get_connected_from(verbs.ACCEPTED)

    # exclude connected
    def get_followers_only(self):
        return self.get_connected_to(verbs.ACCEPTED).exclude(
            id__in=Wizcard.objects.filter(
                requests_from__status=verbs.ACCEPTED,
                requests_from__to_wizcard=self))

    # note: this excludes admin wizcard
    def get_following_only(self):
        return self.get_connected_from(verbs.ACCEPTED).exclude(
            id__in=Wizcard.objects.filter(
                Q(requests_to__status=verbs.ACCEPTED,
                requests_to__from_wizcard=self)| Q(user__profile__is_admin=True)))

    def get_following_no_admin(self):
        return self.get_connected_from(verbs.ACCEPTED).exclude(
            id__in=Wizcard.objects.filter(Q(user__profile__is_admin=True)))

class DeadCard(WizcardBase):
    user = models.ForeignKey(User, related_name="dead_cards")
    first_name = TruncatingCharField(max_length=30, default="")
    last_name = TruncatingCharField(max_length=30, default="")
    invited = models.BooleanField(default=False)
    activated = models.BooleanField(default=False)
    cctx = PickledObjectField(blank=True, default = {})

    def __unicode__(self):
        return _(u'%(user)s\'s deadcard') % {'user': unicode(self.user)}

    def delete(self, *args, **kwargs):
        # incomplete...need to take care of storage cleanup and/or, not deleting
        # but setting a flag instead
        super(DeadCard, self).delete(*args, **kwargs)

    def recognize(self, path):
        ocr = OCR()
        result = ocr.process(path)

        self.first_name = result.get('first_name', "")
        self.last_name = result.get('last_name', "")
        self.phone = result.get('phone', "")
        self.email = result.get('email', "")
        self.ext_fields = dict(web=result.get('web', ""))

        c = self.contact_container.get()
        c.company = result.get('company', "")
        c.title = title=result.get('job', "")

        c.save()
        self.save()

    def set_context(self, cctx):
        self.cctx = cctx
        self.save()

    def get_context(self):
        return self.cctx


class ContactContainer(CompanyTitleMixin):
    wizcard = models.ForeignKey(WizcardBase, related_name="contact_container")
    phone = TruncatingCharField(max_length=20, blank=True)
    media = RelatedObjectsDescriptor()

    def __unicode__(self):
        return (u'%(user)s\'s contact container: %(title)s@ %(company)s \n') % \
               {'user': unicode(self.wizcard.user), 'title': unicode(self.title), 'company': unicode(self.company)}

    class Meta:
        ordering = ['id']

    def get_fbizcard_url(self):
        l = [x.media_element for x in self.media.all().generic_objects() if x.media_sub_type==MediaMixin.SUB_TYPE_F_BIZCARD]
        if l:
            return l

        return ""


class WizConnectionRequest(models.Model):
    from_wizcard = models.ForeignKey(Wizcard, related_name="requests_from")
    to_wizcard = models.ForeignKey(Wizcard, related_name="requests_to")
    cctx = PickledObjectField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=verbs.RELATIONSHIP_STATUSES, default=verbs.PENDING)

    class Meta:
        verbose_name = _(u'wizconnection request')
        verbose_name_plural = _(u'wizconnection requests')
        unique_together = (('to_wizcard', 'from_wizcard'),)

    def __unicode__(self):
        return _(u'%(from_wizcard)s wants to be wizconnections with %(to_wizcard)s') % \
               {'from_wizcard': unicode(self.from_wizcard),
                'to_wizcard': unicode(self.to_wizcard)}

    def accept(self):
        self.status = verbs.ACCEPTED
        self.save()
        signals.wizcardship_accepted.send(sender=self)
        return self

    def decline(self):
        self.status = verbs.DECLINED
        self.save()
        signals.wizcardship_declined.send(sender=self)
        return self

    def reset(self):
        self.status = verbs.PENDING
        self.save()
        return self

    def set_context(self, cctx):
        self.cctx = cctx
        self.save()

    def cancel(self):
        signals.wizcardship_cancelled.send(sender=self)
        #self.delete()

    def fix_context(self):
        if hasattr(self.cctx, '_usercctx'):
            if type(self.cctx.notes) is not dict:
                old_notes = self.cctx.notes
                self.cctx._usercctx = dict(
                    notes = dict(
                        note=old_notes,
                        last_saved=self.created.strftime("%d %B %Y")
                    )
                )
        else:
            self.cctx._usercctx = dict(
                    notes = dict(
                        note="",
                        last_saved=self.created.strftime("%d %B %Y")
                    )
                )
        self.save()


class WizcardFlickManager(models.Manager):
    # Maybe there is a better way to do this. This is defined
    # to allow a callable into fields.py serialization, which needs some
    # state from the callouts here
    tag = None

    def set_tag(self, tag):
        self.tag = tag

    def lookup(self, lat, lng, n, count_only=False):
        flicked_cards = None
        result, count =  LocationMgr.objects.lookup(
            "WTREE",
            lat,
            lng,
            n)
        #convert result to query set result
        if count and not count_only:
            flicked_cards = map(lambda m: self.get(id=m), result)
        return flicked_cards, count

    # def serialize(self, flicked_wizcards,
    #               template=fields.flicked_wizcard_template):
    #     return serialize(flicked_wizcards, **template)
    #
    # def serialize_split(self, my_wizcard, flicked_wizcards):
    #     s = None
    #     own, connected, others = self.split_wizcard_flick(my_wizcard,
    #                                                       flicked_wizcards)
    #
    #     s = dict()
    #     if own:
    #         s['own'] = self.serialize(own)
    #     if connected:
    #         s['connected'] = self.serialize(connected)
    #     if others:
    #         s['others'] = self.serialize(others)
    #
    #     return s
    #
    # def split_wizcard_flick(self, mine, flicked_wizcards):
    #     own = []
    #     connected = []
    #     others = []
    #     for w in flicked_wizcards:
    #         if w.wizcard == mine:
    #             own.append(w)
    #         elif Wizcard.objects.are_wizconnections(w.wizcard, mine):
    #             connected.append(w)
    #         else: others.append(w)
    #
    #     return own, connected, others

    def query_flicks(self, name, phone, email):
        #name can be first name, last name or even combined
        #any of the arguments may be null
        qlist = []

        if name:
            split = name.split()
            for n in split:
                name_result = ((Q(wizcard__first_name__istartswith=n) |
                                Q(wizcard__last_name__istartswith=n)) &
                               Q(expired=False))
                qlist.append(name_result)

        result = self.filter(reduce(operator.or_, qlist))

        return result, len(result)


class WizcardFlick(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    a_created = TruncatingCharField(max_length=40, blank=True)
    wizcard = models.ForeignKey(Wizcard, related_name='flicked_cards')
    timeout = models.IntegerField(default=30)
    lat = models.FloatField(null=True, default=None)
    lng = models.FloatField(null=True, default=None)
    location = generic.GenericRelation(LocationMgr)
    expired = models.BooleanField(default=False)
    reverse_geo_name = TruncatingCharField(max_length=100, default=None)
    #who picked my flicked card?
    flick_pickers = models.ManyToManyField(Wizcard)

    objects = WizcardFlickManager()

    def create_location(self, lat, lng):
        #create
        key = wizlib.create_geohash(lat, lng)
        retval = location.send(sender=self,
                               lat=lat,
                               lng=lng,
                               key=key,
                               tree="WTREE")
        loc= retval[0][1]

        return loc

    # AA: TODO. The whole flick thing needs to be revisited anyway.
    def delete(self, *args, **kwargs):
        notif = kwargs.pop('type', None)
        self.location.get().delete()

        if notif[0] == verbs.WIZCARD_FLICK_TIMEOUT[0]:
            #timeout
            logger.debug('timeout flicked wizcard %s', self.id)
            self.expired = True
            self.save()
            notify.send(
                self.wizcard.user,
                recipient=self.wizcard.user,
                notif_tuple=verbs.WIZCARD_FLICK_TIMEOUT,
                target=self,
                delivery_type=BaseNotification.DELIVERY_TYPE_SYNC
            )
        else:
            #withdraw/delete flick case
            logger.debug('withdraw flicked wizcard %s', self.id)
            super(WizcardFlick, self).delete(*args, **kwargs)

    def get_tag(self):
        return WizcardFlick.objects.tag

    def time_remaining(self):
        if not self.expired:
            return self.location.get().timer.get().time_remaining()
        else:
            return 0


class UserBlocks(models.Model):
    user = models.ForeignKey(User, related_name='user_blocks')
    blocks = models.ManyToManyField(User, related_name='blocked_by_set')

    class Meta:
        verbose_name = verbose_name_plural = _(u'user blocks')

    def __unicode__(self):
        return _(u'Users blocked by %(user)s') % {'user': unicode(self.user)}

    def block_count(self):
        return self.blocks.count()
    block_count.short_description = _(u'Blocks count')

    def block_summary(self, count=7):
        block_list = self.blocks.all()[:count]
        return u'[%s%s]' % (u', '.join(unicode(user) for user in block_list),
                            u', ...' if self.block_count() > count else u'')
    block_summary.short_description = _(u'Summary of blocks')


# Signal connections

#models.signals.post_save.connect(signals.create_wizcardship_instance,
#                                 sender=User,
#                                 dispatch_uid='cards.signals.create_' \
#                                              'wizcardship_instance')
#models.signals.post_save.connect(signals.create_userblocks_instance,
#                                 sender=User,
#                                 dispatch_uid='cards.signals.create_' \
#                                              'userblocks_instance')
