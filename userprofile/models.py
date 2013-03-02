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
from lib import wizlib
import string
import random
import pdb

ptree = trie()

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

    objects = UserProfileManager()

    def is_future(self):
        return self.future_user

    def set_future(self):
        self.future_user = True
        self.save()

    def get_location(self):
        location_qs = self.location.all()
        if location_qs:
            return location_qs[0]
        else:
            return None

    def create_or_update_location(self, lat, lng):
        l = self.get_location()
        if l:
            l.do_update(lat, lng, ptree)
        else:
            #create
            key = wizlib.create_geohash(lat, lng)
            location.send(sender=self, lat=lat, lng=lng, key=key, tree=ptree)

    def lookup(self, n, count_only=False):
        users = None
        l = self.get_location()
        result, count = LocationMgr.objects.lookup_by_key(ptree, 
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

