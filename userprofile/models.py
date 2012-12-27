from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from location_mgr.models import LocationMgr
from pytrie import SortedStringTrie as trie

import pdb

ptree = trie()
class UserProfile(LocationMgr):
    # This field is required.
    user = models.OneToOneField(User, related_name='profile')

    def save(self, *args, **kwargs):
        super(UserProfile, self).save(tree=ptree, *args, **kwargs)

    def update(self, *args, **kwargs):
        super(UserProfile, self).update(tree=ptree, *args, **kwargs)

    def serialize_objects(self):
        #add callouts to all serializable objects here
        wizcard = []
        wizconnections = []
        try:
            qs = self.user.wizcard
        except:
            return None, None

        #wizcards
        wizcard = serialize(qs, **fields.wizcard_template)

        #wizconnections
        if qs.wizconnections.count():
            wizconnections = qs.serialize_wizconnections()


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

