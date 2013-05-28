from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from lib.pytrie import SortedStringTrie as trie
from lib.preserialize.serialize import serialize
from wizserver import fields
from location_mgr.models import location, LocationMgr
from django.contrib.contenttypes import generic
from wizcardship.models import Wizcard
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.conf import settings
from lib import wizlib
import datetime
import string
import random
import pdb

class UserProfileManager(models.Manager):
    def serialize(self, users):
        return serialize(users, **fields.user_query_template)

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
    userid = models.CharField(max_length=100)
    future_user = models.BooleanField(default=False, blank=False)
    location = generic.GenericRelation(LocationMgr)

    #AA:TODO: should be extended into a 1:many for supporting multiple devices
    IOS = 'ios'
    ANDROID='android'
    DEVICE_CHOICES = (
	(IOS, 'iPhone'),
	(ANDROID, 'Android'),
    )
    device_type = models.CharField(max_length=10, 
		    		   choices=DEVICE_CHOICES, 
				   default=IOS)
    device_id = models.CharField(max_length=30)
    reg_token = models.CharField(max_length=30)

    objects = UserProfileManager()

    def last_seen(self):
        return cache.get('seen_%s' % self.user.username)

    def online(self):
        if self.last_seen():
            now = datetime.datetime.now()
            if now > self.last_seen() + datetime.timedelta(
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

    def get_location(self):
        location_qs = self.location.all()
        if location_qs:
	    #AA_TODO: ideally should only be 1 object present..check why/when it'll be more
            return location_qs[0]
        else:
            return None

    def create_or_update_location(self, lat, lng):
        l = self.get_location()
        if l:
            updated = l.do_update(lat, lng)
	    if not updated:
                #reset the timer
                l.reset_timer()
            else:
                #updated location, so key must have changed, need to re-install timer
                l.destroy_timer()
		l.start_timer(timeout=10, l_id=l.id)
	    return l
        else:
            #create
            key = wizlib.create_geohash(lat, lng)
            l_tuple = location.send(sender=self, lat=lat, lng=lng, key=key, 
                                    tree=LocationMgr.objects.PTREE)
	    l_tuple[1].start_timer(timeout=10, 
                                   key=l_tuple[1].id)

    def lookup(self, n, count_only=False):
        users = None
        l = self.get_location()
        result, count = LocationMgr.objects.lookup_by_key(
                            l.tree_type,
                            l.key, 
                            n)
        #convert result to query set result
        if count and not count_only:
            users = map(lambda m: UserProfile.objects.get(id=m).user, result)
        return users, count

    def serialize(self, users):
        return serialize(users, **fields.user_query_template)


    def serialize_objects(self):
        #add callouts to all serializable objects here
        w = None
        wc = None
        try:
            qs = self.user.wizcard
        except:
            return w, wc

        #wizcards
        w = Wizcard.objects.serialize(qs)

        #wizconnections
        if qs.wizconnections.count():
            wc = qs.serialize_wizconnections()

        return w, wc


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

