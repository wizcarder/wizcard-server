from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from lib.pytrie import SortedStringTrie as trie
from lib.preserialize.serialize import serialize
from wizserver import fields
from location_mgr.models import location, LocationMgr
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from wizcardship.models import Wizcard
from virtual_table.models import VirtualTable
from django.core.exceptions import ObjectDoesNotExist
import operator
from django.db.models import Q
from django.core.cache import cache
from django.conf import settings
from lib import wizlib
from django.utils import timezone
import string
import random
import pdb

USER_ACTIVE_TIMEOUT = 10

class UserProfileManager(models.Manager):
    def serialize_split(self, me, users, send_data=True):
	s = dict()
        if send_data:
            template = fields.wizcard_template_brief_with_thumbnail
        else:
            template = fields.wizcard_template_brief

	own, connected, others = self.split_users(me, users)
        if own:
            s['own'] = UserProfile.objects.serialize(own, template)
        if connected:
            s['connected'] = UserProfile.objects.serialize(connected, template)
        if others:
            s['others'] = UserProfile.objects.serialize(others, template)

        return s

    def split_users(self, me, users):
        connected = []
        own = []
	others = []
        for user in users:
            if Wizcard.objects.are_wizconnections(user.wizcard, me.wizcard):
                connected.append(user)
            elif user == me:
                own.append(user)
            else:
                others.append(user)
        return own, connected, others

    def serialize(self, users, template):
        wizcards = map(lambda u: u.wizcard, users)
        return serialize(wizcards, **template)

    def id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        userid =  ''.join(random.choice(chars) for x in range(size))
        try:
            User.objects.get(username=userid)
            userid = self.id_generator()
        except ObjectDoesNotExist:
            pass
        return userid

    def gen_password(self, id1, id2, id3=None):
        return id2
    
    def username_from_phone_num(self, phone_num):
        return phone_num + settings.WIZCARD_USERNAME_EXTENSION

    def futureusername_from_phone_num(self, phone_num):
        return phone_num + settings.WIZCARD_FUTURE_USERNAME_EXTENSION

class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User, related_name='profile')
    activated = models.BooleanField(default=False)
    #this is the internal userid
    userid = models.CharField(max_length=100)
    future_user = models.BooleanField(default=False, blank=False)
    location = generic.GenericRelation(LocationMgr)
    do_sync = models.BooleanField(default=False)
    is_profile_private = models.BooleanField(default=False)
    is_wifi_data = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    block_unsolicited = models.BooleanField(default=False)

    IOS = 'ios'
    ANDROID='android'
    DEVICE_CHOICES = (
	(IOS, 'iPhone'),
	(ANDROID, 'Android'),
    )
    device_type = models.CharField(max_length=10, 
		    		   choices=DEVICE_CHOICES, 
				   default=IOS)
    device_id = models.CharField(max_length=100)
    reg_token = models.CharField(max_length=100)

    objects = UserProfileManager()

    def online_key(self):
        return self.userid

    def online(self):
        cache.set(settings.USER_ONLINE_PREFIX % self.online_key(), timezone.now(), 
                settings.USER_LASTSEEN_TIMEOUT)

    def can_send_data(self, on_wifi):
        return (True if on_wifi else not(self.is_wifi_data))

    def last_seen(self):
        now = timezone.now()
        ls = cache.get(settings.USER_ONLINE_PREFIX % self.online_key())
        if bool(ls):
            return(True, (now - ls))
        else:
            return(False, None)

    def is_online(self):
        on, ls = self.last_seen()
        delta = timezone.timedelta(seconds=settings.USER_ONLINE_TIMEOUT)
        if on and (ls < delta):
            return True
        return False

    def is_future(self):
        return self.future_user

    def set_future(self):
	self.activated = False
        self.future_user = True
        self.save()

    def is_ios(self):
        return bool(self.device_type == self.IOS)

    def create_or_update_location(self, lat, lng):
        try:
            l = self.location.get()
            updated = l.do_update(lat, lng)
            l.reset_timer()
	    return l
        except ObjectDoesNotExist:
            #create
            l_tuple = location.send(sender=self, lat=lat, lng=lng, 
                                    tree="PTREE")
	    l_tuple[0][1].start_timer(USER_ACTIVE_TIMEOUT)

    def lookup(self, n, count_only=False):
        users = None
        try:
            l = self.location.get()
        except ObjectDoesNotExist:
            return None, None

        result, count = l.lookup(n)
        #convert result to query set result
        if count and not count_only:
            users = [UserProfile.objects.get(id=x).user for x in result if UserProfile.objects.filter(id=x, activated=True, is_visible=True).exists()]
        return users, count

    def serialize_objects(self):
        s = {}
        #add callouts to all serializable objects here

	#wizcard
        try:
	    wizcard = self.user.wizcard
            w = wizcard.serialize()
            s['wizcard'] = w
        except ObjectDoesNotExist:
            return s

        #flicks (put flicked before wizconnections since wizconnection 
	#could refer to flicks)
	if wizcard.flicked_cards.count():
	    wf = wizcard.serialize_wizcardflicks()
	    s['wizcard_flicks'] = wf

        #wizconnections
        if wizcard.wizconnections.count():
            wc = wizcard.serialize_wizconnections()
	    s['wizconnections'] = wc


        #tables
        tables = self.user.tables.all()
	if tables.count():
	    # serialize created and joined tables
            tbls = VirtualTable.objects.serialize_split(
                    tables, 
                    self.user,
                    fields.table_template)
	    s['tables'] = tbls

        return s

class FutureUserManager(models.Manager):
    def check_future_user(self, email=None, phone=None):
        qlist = []
        if email:
            qlist.append(Q(email=email))
        if phone:
            qlist.append(Q(phone=phone))
        return self.filter(reduce(operator.or_, qlist))

class FutureUser(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    asset_type = models.CharField(max_length=20, blank=False)

    objects = FutureUserManager()

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile(user=instance)
	profile.userid = UserProfile.objects.id_generator()
        profile.save()

post_save.connect(create_user_profile, sender=User)

