from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from location_mgr.models import LocationMgr
from pytrie import SortedStringTrie as trie
from preserialize.serialize import serialize
from wizserver import fields

import pdb

ptree = trie()

class UserProfileManager(models.Manager):
    def lookup(self, key, n):
        result, count = UserProfile.objects.lookup_by_key(tree=ptree, key=key, num_results=n)
        #convert result to query set result
        users = map(lambda m: self.get(id=m).user, result)
        return users, count

class UserProfile(LocationMgr):
    # This field is required.
    user = models.OneToOneField(User, related_name='profile')

    default_manager = UserProfileManager()

    def save(self, *args, **kwargs):
        super(UserProfile, self).save(tree=ptree, *args, **kwargs)
        print 'saving to tree [{ptree}]'.format (ptree=ptree)

    def update(self, *args, **kwargs):
        super(UserProfile, self).update(tree=ptree, *args, **kwargs)
        print 'updating to tree [{ptree}]'.format (ptree=ptree)

    def serialize_objects(self):
        #add callouts to all serializable objects here
        w = None
        wc = None
        try:
            qs = self.user.wizcard
        except:
            return w, wc

        #wizcards
        w = qs.serialize()

        #wizconnections
        if qs.wizconnections.count():
            wc = qs.serialize_wizconnections()

        return w, wc


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

