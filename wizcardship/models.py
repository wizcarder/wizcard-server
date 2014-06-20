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


import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
import signals
import pdb
from django.db.models import Q
from django.core.files.base import ContentFile
from lib.preserialize.serialize import serialize
from wizserver import fields
from lib.pytrie import SortedStringTrie as trie
from django.contrib.contenttypes import generic
from django.core.exceptions import ObjectDoesNotExist
from location_mgr.models import location, LocationMgr
from django.http import HttpResponseBadRequest, Http404
from notifications.signals import notify
from django.core.files.storage import default_storage
from django.conf import settings
import operator
from django.db.models import Q
from lib import wizlib
from wizcard import err
from django.db.models import ImageField


class WizcardManager(models.Manager):
    def except_wizcard(self, except_user):
        qs = Wizcard.objects.filter(~Q(user=except_user))
        return qs 
		
    def wizconnections_of(self, user, shuffle=False):
        qs = User.objects.filter(wizcard__wizconnections__user=user)
        if shuffle:
            qs = qs.order_by('?')
        return qs

    def are_wizconnections(self, wizcard1, wizcard2):
        return bool((wizcard1.wizconnections.filter(
            id=wizcard2.id)).exists())

    def wizconnection_req_clear(self, from_wizcard, to_wizcard):
        WizConnectionRequest.objects.filter(from_wizcard=from_wizcard,
                                            to_wizcard=to_wizcard).delete()

		
    def becard(self, wizcard1, wizcard2):
        wizcard1.wizconnections.add(wizcard2)
        # Now that user1 accepted user2's card request we should delete any
        # request by user1 to user2 so that we don't have ambiguous data
        WizConnectionRequest.objects.filter(from_wizcard=wizcard1,
                                            to_wizcard=wizcard2).delete()

    def uncard(self, wizcard1, wizcard2):
        # Break cardship link between users
        wizcard1.wizconnections.remove(wizcard2)
        # Delete Wizcconnection request as well
        self.wizconnection_req_clear(wizcard1, wizcard2)
        self.wizconnection_req_clear(wizcard2, wizcard1)

    def accept_wizconnection(self, from_wizcard, to_wizcard):
        WizConnectionRequest.objects.filter(from_wizcard=from_wizcard,
                to_wizcard=to_wizcard).get().accept()

    def serialize(self, wizcards, template):
        return serialize(wizcards, **template)

    def exchange_implicit(self, wizcard1, wizcard2, flick_card):
        source_user = wizcard1.user
        target_user = wizcard2.user

        self.becard(wizcard1, wizcard2) 
        self.becard(wizcard2, wizcard1) 
        #Q this to the receiver and vice-versa
        notify.send(source_user, recipient=target_user,
                    verb='wizconnection request trusted', 
		    description='via flick pick',
                    target=wizcard1, action_object=wizcard2)
        notify.send(target_user, recipient=source_user,
                    verb='wizconnection request trusted', 
		    description='via flick pick',
                    target=wizcard2, action_object=flick_card)

    def exchange_explicit(self, wizcard1, wizcard2):
        source_user = wizcard1.user
        target_user = wizcard2.user
        convert_to_implicit = False

        # If there's a wizconnection request from the other user then treat it like
        # an implicit connection
        try:
            self.accept_wizconnection(wizcard2, wizcard1)
            convert_to_implicit = True
        except ObjectDoesNotExist:
            try: 
                wizconnection = WizConnectionRequest.objects.create(
                    from_wizcard=wizcard1,
                    to_wizcard=wizcard2,
                    message="wizconnection request") 
                #Q this to the receiver 
            except:
                #duplicate request
                #nothing to do, just return silently
                return
        #send notifs to recipient (or both if implicit conversion)
        if convert_to_implicit:
            notify.send(source_user, recipient=target_user, 
                    verb='wizconnection request trusted', 
                    target=wizcard1, action_object=wizcard2)

            notify.send(target_user, recipient=source_user, 
                    verb='wizconnection request trusted', 
                    target=wizcard2, action_object=wizcard1)

        else:
            notify.send(source_user, recipient=target_user, 
                    verb='wizconnection request untrusted', 
                    target=wizcard1, action_object=wizcard2)

    def exchange(self, wizcard1, wizcard2, implicit, flick_card=None):
        #create bidir cardship
        if self.are_wizconnections(wizcard1, wizcard2):
            return  err.EXISTING_CONNECTION
        elif implicit:
            self.exchange_implicit(wizcard1, wizcard2, flick_card)
        else:
            self.exchange_explicit(wizcard1, wizcard2)
        return err.OK

    def update_wizconnection(self, wizcard1, wizcard2):
        notify.send(wizcard1.user, recipient=wizcard2.user,
                    verb='wizcard update',
                    target=wizcard1, action_object=wizcard2)
        
    def query_users(self, userID, name, phone, email):
        #name can be first name, last name or even combined
        #any of the arguments may be null
        qlist = []

        if name != None:
            split = name.split()
            for n in split:
                name_result = (Q(first_name__istartswith=n) | Q(last_name__istartswith=n))
                qlist.append(name_result)

        #phone
        if phone != None:
            phone_result = (Q(phone=phone) | Q(phone2__startswith=phone))
            qlist.append(phone_result)

        #email
        if email != None:
            email_result = Q(email=email)
            qlist.append(email_result)

        result = self.filter(reduce(operator.or_, qlist)).exclude(user_id=userID)

        return result, len(result)

    def migrate_future_user(self, future, current):
        WizConnectionRequest.objects.filter(to_wizcard=future.wizcard).update(to_wizcard=current.wizcard.pk)

class Wizcard(models.Model):
    user = models.OneToOneField(User, related_name='wizcard')
    wizconnections = models.ManyToManyField('self', symmetrical=True, blank=True)
    first_name = models.CharField(max_length=40, blank=True)
    last_name = models.CharField(max_length=40, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    #media objects
    thumbnailImage = models.ImageField(upload_to="image/")
    video = models.FileField(upload_to="video/")

    objects = WizcardManager()

    class Meta:
        verbose_name = _(u'wizcard')
        verbose_name_plural = _(u'wizcards')

    def __unicode__(self):
        return _(u'%(user)s\'s wizcard') % {'user': unicode(self.user)}

    def serialize(self):
        return serialize(self, **fields.wizcard_template_extended)

    def serialize_wizconnections(self):
        return serialize(self.wizconnections.all(), **fields.wizcard_template_extended)

    def serialize_wizcardflicks(self):
	return serialize(self.flicked_cards.all(), **fields.my_flicked_wizcard_template)

    def create_company_list(self, l):
        map(lambda x: CompanyList(wizcard=self, company=x).save(), l)

    def create_designation_list(self, l):
        map(lambda x: DesignationList(wizcard=self, designation=x).save(), l)

    def create_wizcard_image_list(self, l):
        map(lambda x: WizcardImageList(wizcard=self, image=x).save(), l)

    def get_latest_company(self):
        return self.contact_container.all()[0].company

    def get_latest_title(self):
        return self.contact_container.all()[0].title
        
    def wizconnection_count(self):
        return self.wizconnections.count()
    wizconnection_count.short_description = _(u'Cards count')

    def wizconnection_summary(self, count=7):
        wizconnection_list = self.wizconnections.all().select_related(depth=1)[:count]
        return u'[%s%s]' % (u', '.join(unicode(f.user) for f in wizconnection_list),
                            u', ...' if self.wizconnection_count() > count else u'')
    wizconnection_summary.short_description = _(u'Summary of wizconnections')

    def flood(self):
        for wizcard in self.wizconnections.all():
            Wizcard.objects.update_wizconnection(self, wizcard)

    def check_flick_duplicates(self, lat, lng):
	#check if nearby cards can be combined...do we need to adjust centroid and all that ?
        for w in self.flicked_cards.all():
            if wizlib.haversine(w.lng, w.lat, lng, lat) < settings.WIZCARD_FLICK_AGGLOMERATE_RADIUS:
                return w
        return None

class ContactContainer(models.Model):
    wizcard = models.ForeignKey(Wizcard, related_name="contact_container")
    company = models.CharField(max_length=40, blank=True)
    title = models.CharField(max_length=200, blank=True)
    start = models.CharField(max_length=30, blank=True)
    end = models.CharField(max_length=30, blank=True)
    f_bizCardImage = models.ImageField(upload_to="image/")
    r_bizCardImage = models.ImageField(upload_to="image/")

    def __unicode__(self):
        return _(u'%(user)s\'s contact container: %(title)s@ %(company)s \n') % {'user': unicode(self.wizcard.user), 'title': unicode(self.title), 'company': unicode(self.company)} 

    class Meta:
        ordering = ['id']


class WizConnectionRequest(models.Model):
    from_wizcard = models.ForeignKey(Wizcard, related_name="invitations_from")
    to_wizcard = models.ForeignKey(Wizcard, related_name="invitations_to")
    message = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        verbose_name = _(u'wizconnection request')
        verbose_name_plural = _(u'wizconnection requests')
        unique_together = (('to_wizcard', 'from_wizcard'),)

    def __unicode__(self):
        return _(u'%(from_wizcard)s wants to be wizconnections with %(to_wizcard)s') % \
                    {'from_wizcard': unicode(self.from_wizcard),
                     'to_wizcard': unicode(self.to_wizcard)}

    def accept(self):
        Wizcard.objects.becard(self.from_wizcard, self.to_wizcard)
        self.accepted = True
        self.save()
        signals.wizcardship_accepted.send(sender=self)

    def decline(self):
        signals.wizcardship_declined.send(sender=self)
        self.delete()

    def cancel(self):
        signals.wizcardship_cancelled.send(sender=self)
        self.delete()

class WizcardFlickManager(models.Manager):

    #AA:TODO: Maybe there is a better way to do this. This is defined
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

    def serialize(self, flicked_wizcards, merge=False):
        template = fields.flicked_wizcard_merged_template if merge else fields.flicked_wizcard_template
        return serialize(flicked_wizcards, **template)

    def serialize_split(self, my_wizcard, flicked_wizcards, merge=False, flatten=False):

        s = None
	own, connected, others = self.split_wizcard_flick(my_wizcard, flicked_wizcards)

        if flatten:
            s = []
            if own:
                self.set_tag("own")
                s += self.serialize(own, merge)
            if connected:
                self.set_tag("connected")
                s += self.serialize(connected, merge)
            if others:
                self.set_tag("others")
                s += self.serialize(others, merge)
            self.set_tag(None)
        else:
            s = dict()
            if own:
                s['own'] = self.serialize(own, merge)
            if connected:
                s['connected'] = self.serialize(own, merge)
            if others:
                s['others'] = self.serialize(others, merge)

	return s

    def split_wizcard_flick(self, mine, flicked_wizcards):
        own = []
        connected = []
	others = []
	for w in flicked_wizcards:
            if w.wizcard == mine:
	        own.append(w)
	    elif Wizcard.objects.are_wizconnections(w.wizcard, mine):
	        connected.append(w)
            else: others.append(w)

	return own, connected, others


    def query_flicks(self, name, phone, email):
        #name can be first name, last name or even combined
        #any of the arguments may be null
        qlist = []

        if name != None:
            split = name.split()
            for n in split:
                name_result = (Q(wizcard__first_name__istartswith=n) | Q(wizcard__last_name__istartswith=n))
                qlist.append(name_result)

        result = self.filter(reduce(operator.or_, qlist))

        return result, len(result)


class WizcardFlick(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    a_created = models.CharField(max_length=40, blank=True)
    wizcard = models.ForeignKey(Wizcard, related_name='flicked_cards')
    timeout = models.IntegerField(default=30)
    lat = models.FloatField(null=True, default=None)
    lng = models.FloatField(null=True, default=None)
    location = generic.GenericRelation(LocationMgr)
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
        print 'new flicked card location at [{lat}, {lng}]'.format (lat=lat, lng=lng)
        loc= retval[0][1]

        return loc

    def delete(self, *args, **kwargs):
        print 'deleting flicked wizcard', self.id
        #AA:TODO - For some reason, django doesn't call delete method of generic FK object.
        # Although it does delete it. Until I figure out why, need to explicitly call 
        #delete method since other deletes need to happen there as well
        self.location.get().delete()
	notify.send(self.wizcard.user, recipient=self.wizcard.user, verb ='flick timeout', target=self, action_object=self.wizcard)
        super(WizcardFlick, self).delete(*args, **kwargs)

    def get_tag(self):
        return WizcardFlick.objects.tag

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
