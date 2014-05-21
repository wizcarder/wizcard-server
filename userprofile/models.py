from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from lib.pytrie import SortedStringTrie as trie
from lib.preserialize.serialize import serialize
from wizserver import fields
from location_mgr.models import location, LocationMgr
from django.contrib.contenttypes import generic
from wizcardship.models import Wizcard
from virtual_table.models import VirtualTable
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.conf import settings
from lib import wizlib
from django.utils import timezone
import string
import random
import pdb

USER_ACTIVE_TIMEOUT = 10

class UserProfileManager(models.Manager):
    def serialize(self, users, include_thumbnail=False):
        wizcards = map(lambda u: u.wizcard, users)
        if include_thumbnail:
            #return serialize(wizcards, **fields.wizcard_template_thumbnail)
            return serialize(wizcards, **fields.wizcard_template)
        else:
            return serialize(wizcards, **fields.wizcard_template)

    def id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        userid =  ''.join(random.choice(chars) for x in range(size))
        try:
            User.objects.get(username=userid)
            userid = self.id_generator()
        except ObjectDoesNotExist:
            pass
        return userid

class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User, related_name='profile')
    #this is the internal userid
    userid = models.CharField(max_length=100)
    future_user = models.BooleanField(default=False, blank=False)
    location = generic.GenericRelation(LocationMgr)
    do_sync = models.BooleanField(default=False)

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

    def last_seen(self):
        return cache.get('seen_%s' % self.user.username)

    def online(self):
        if self.last_seen():
            now = timezone.now()
            if now > self.last_seen() + timezone.timedelta(
                seconds=settings.USER_ONLINE_TIMEOUT):
                return False
            else: 
                return True
        else:
            return False

    def is_future(self):
        return self.future_user

    def set_future(self):
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
            key = wizlib.create_geohash(lat, lng)
            l_tuple = location.send(sender=self, lat=lat, lng=lng, key=key, 
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
            users = map(lambda m: UserProfile.objects.get(id=m).user, result)
        return users, count

    def serialize_objects(self):
        s = {}
        #add callouts to all serializable objects here

	#wizcard
        try:
	    wizcard = self.user.wizcard
            w = Wizcard.objects.serialize(wizcard)
            s['wizcard'] = w
        except ObjectDoesNotExist:
            return s

        #wizconnections
        if wizcard.wizconnections.count():
            wc = wizcard.serialize_wizconnections()
	    s['wizconnections'] = wc

        #flicks
	if wizcard.flicked_cards.count():
	    wf = wizcard.serialize_wizcardflicks()
	    s['wizcard_flicks'] = wf

        #tables
        tables = self.user.tables.all()
	if tables.count():
	    # serialize created and joined tables
            tbls = VirtualTable.objects.serialize_split(tables, self.user)
	    s['tables'] = tbls

        return s


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

