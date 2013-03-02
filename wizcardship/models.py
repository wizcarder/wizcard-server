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
from location_mgr.models import location, LocationMgr
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest, Http404
from notifications.models import notify
from django.core.files.storage import default_storage
import operator
from django.db.models import Q
from lib import wizlib
#from django.db.models import ImageField

wtree = trie()

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
        get_object_or_404(WizConnectionRequest, from_wizcard=from_wizcard,
                          to_wizcard=to_wizcard).accept()

    def serialize(self, wizcards):
        return serialize(wizcards, **fields.wizcard_template)


    def exchange_implicit(self, wizcard1, wizcard2):
        source_user = wizcard1.user
        target_user = wizcard2.user

        self.becard(wizcard1, wizcard2) 
        self.becard(wizcard2, wizcard1) 
        #Q this to the receiver and vice-versa
        notify.send(source_user, recipient=wizcard2.user,
                    verb='wizconnection request trusted', 
                    target=wizcard1, action_object=wizcard2)
        notify.send(wizcard2.user, recipient=source_user,
                    verb='wizconnection request trusted', 
                    target=wizcard2, action_object=wizcard1)

    def exchange_explicit(self, wizcard1, wizcard2):
        source_user = wizcard1.user
        target_user = wizcard2.user

        #send a connection request
        try:
            # If there's a wizconnection request from the other user accept it.
            self.accept_wizconnection(wizcard2, wizcard1)
        except Http404:
            # If we already have an active wizconnection request IntegrityError
            # will be raised and the transaction will be rolled back.
            try: 
                wizconnection = WizConnectionRequest.objects.create(
                    from_wizcard=wizcard1,
                    to_wizcard=wizcard2,
                    message="wizconnection request") 
                #Q this to the receiver 
                notify.send(source_user, recipient=target_user, 
                            verb='wizconnection request untrusted', 
                            target=wizcard1, action_object=wizcard2)
            except: #AA: TODO: Put integrity error
                #nothing to do, just return silently
                pass 


    def exchange(self, wizcard1, wizcard2, implicit):
        #create bidir cardship
        ret = dict(Error="OK", Description="")
        if self.are_wizconnections(wizcard1, wizcard2):
            ret['Error'] = 2
            ret['Description'] = "Already connected to user"
        elif implicit:
            self.exchange_implicit(wizcard1, wizcard2)
        else:
            self.exchange_explicit(wizcard1, wizcard2)
        return ret

    def update_wizconnection(self, wizcard1, wizcard2):
        notify.send(wizcard1.user, recipient=wizcard2.user,
                    verb='wizcard update',
                    target=wizcard1, action_object=wizcard2)
        
    def find_users(self, userID, name, phone, email):
        #name can be first name, last name or even combined
        #any of the arguments may be null
        qlist = []

        if name != None:
            split = name.split()
            for n in split:
                name_result = (Q(first_name__icontains=n) | Q(last_name__icontains=n))
                qlist.append(name_result)

        #phone
        if phone != None:
            phone_result = (Q(phone1__contains=phone) | Q(phone2__contains=phone))
            qlist.append(phone_result)

        #email
        if email != None:
            email_result = Q(email=email)
            qlist.append(email_result)

        result = self.filter(reduce(operator.or_, qlist)).exclude(user_id=userID)

        return result, len(result)

    def migrate_future_user(self, future, current):
        WizConnectionRequest.objects.filter(to_wizcard=future.wizcard).update(to_wizcard=current.wizcard.pk)

    def lookup(self, lat, lng, n, count_only=False):
        wizcards = None
        result, count =  LocationMgr.objects.lookup_by_lat_lng(wtree, 
                                                               lat, 
                                                               lng, 
                                                               n)
        #convert result to query set result
        #AA:TODO: filter out self and connected
        if count and not count_only:
            wizcards = map(lambda m: self.get(id=m), result)
        return wizcards, count


class Wizcard(models.Model):
    user = models.OneToOneField(User, related_name='wizcard')
    wizconnections = models.ManyToManyField('self', symmetrical=True, blank=True)
    first_name = models.CharField(max_length=40, blank=True)
    last_name = models.CharField(max_length=40, blank=True)
    phone1 = models.CharField(max_length=20, blank=True)
    phone2 = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address_street1 = models.CharField(max_length=40, blank=True)
    address_city = models.CharField(max_length=40, blank=True)
    address_state = models.CharField(max_length = 20, blank=True)
    address_country = models.CharField(max_length = 20, blank=True)
    address_zip = models.CharField(max_length = 20, blank=True)
    #media objects
    #AA:TODO: This(image/video management) is quite primitive
    thumbnailImage = models.ImageField(upload_to="image/")
    video = models.FileField(upload_to="video/")
    locations = generic.GenericRelation(LocationMgr)

    objects = WizcardManager()

    class Meta:
        verbose_name = _(u'wizcard')
        verbose_name_plural = _(u'wizcards')

    def __unicode__(self):
        return _(u'%(user)s\'s wizcard') % {'user': unicode(self.user)}

    def serialize_wizconnections(self):
        return serialize(self.wizconnections.all(), **fields.wizcard_template)


    def create_company_list(self, l):
        map(lambda x: CompanyList(wizcard=self, company=x).save(), l)

    def create_designation_list(self, l):
        map(lambda x: DesignationList(wizcard=self, designation=x).save(), l)

    def create_wizcard_image_list(self, l):
        map(lambda x: WizcardImageList(wizcard=self, image=x).save(), l)

    def company_list(self):
        self.company_list.all()

    def designation_list(self):
        self.designation_list.all()
        
    def wizcard_image_list(self):
        self.wizcard_image_list.all()
        
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

    def get_location(self):
        return self.location.all()

    def get_or_create_location(self, lat, lng):
        created = True
        try:
            location_qs = self.locations.get(lat=lat, 
                                             lng=lng) 
            created = False
            #AA:TODO: For now, check for wtree and re-populate if not there (server 
            #restart) this eventually needs to come from db read during init
            if not wtree.has_key(location_qs.key):
                wtree[location_qs.key] = location_qs.object_id
        except:
            #create
            key = wizlib.create_geohash(lat, lng)
            location_qs = location.send(sender=self, 
                                        lat=lat, 
                                        lng=lng, 
                                        key=key, 
                                        tree=wtree)
            print 'new flicked card location at [{lat}, {lng}]'.format (lat=lat, lng=lng)

        return location_qs, created


class ContactContainer(models.Model):
    wizcard = models.ForeignKey(Wizcard, related_name="contact_container")
    company = models.CharField(max_length=40, blank=True)
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to="image/")
    def __unicode__(self):
        return _(u'%(user)s\'s contact container') % {'user': unicode(self.wizcard.user)}



    class Meta:
        ordering = ['id']


class WizConnectionRequest(models.Model):
    from_wizcard = models.ForeignKey(Wizcard, related_name="invitations_from")
    to_wizcard = models.ForeignKey(Wizcard, related_name="invitations_to")
    message = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(default=datetime.datetime.now,
                                   editable=False)
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
