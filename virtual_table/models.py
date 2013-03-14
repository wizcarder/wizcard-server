from django.db import models

# Create your models here.
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
from django.contrib.auth.models import User
import pdb
from django.db.models import Q
from datetime import datetime
from lib import wizlib
from lib.pytrie import SortedStringTrie as trie
from location_mgr.models import location, LocationMgr
from wizcardship.models import Wizcard
from django.contrib.contenttypes import generic
from lib.preserialize.serialize import serialize
from wizserver import fields
from virtual_table.signals import virtualtable_vtree_timeout

vtree = trie()

class VirtualTableManager(models.Manager):
    def lookup(self, lat, lng, n, count_only=False):
        tables = None
        result, count = LocationMgr.objects.lookup_by_lat_lng(vtree, 
                                                              lat,
                                                              lng,
                                                              n)
        #convert result to query set result
        if count and not count_only:
            tables = map(lambda m: self.get(id=m), result)
        return tables, count

    def serialize(self, tables):
        return serialize(tables, **fields.table_template)


class VirtualTable(models.Model):
    tablename = models.CharField(max_length=40)
    numSitting = models.IntegerField(default=0, blank=True)
    secureTable = models.BooleanField(default=False)
    password = models.CharField(max_length=40, blank=True)
    creator = models.ForeignKey(User, related_name='tables')
    users = models.ManyToManyField(User, through='Membership')
    life_time = models.IntegerField(default=30)
    location = generic.GenericRelation(LocationMgr)

    objects = VirtualTableManager()

    def __unicode__(self):
        return self.tablename

    def get_location(self):
        location_qs = self.location.all()
        if location_qs:
            return location_qs[0]
        else:
            return None

    def create_location(self, lat, lng):
        key = wizlib.create_geohash(lat, lng)
        location.send(sender=self, lat=lat, lng=lng, key=key, tree=vtree)

    def isSecure(self):
        return self.secureTable

    def table_exchange(self, joinee):
        joined = self.users.all().exclude(id=joinee.id)
        wizcard1 = User.objects.get(id=joinee.pk).wizcard

        wizcards = map(lambda u: User.objects.get(id=u.pk).wizcard, joined)
        implicit_exchange = self.isSecure()

        for wizcard2 in wizcards:
            Wizcard.objects.exchange(wizcard1, wizcard2, implicit_exchange)

        return self

    def name(self):
        return self.tablename

    def join_table_and_exchange(self, user, password, do_exchange):
        #check password
        if self.password == password:
            m, created = Membership.objects.get_or_create(user=user, table=self)
            self.inc_numsitting()
            if do_exchange is True:
                self.table_exchange(user)
        else:
            return None
        return self

    def leave_table(self, user):
        try:
            user.membership_set.get(table=self).delete()
        except:
            pass
        else:
            self.dec_numsitting()

        #we can destroy this table if no one is active
        if self.numSitting == 0:
            self.delete()
        return self

    def delete_table(self, user):
        self.users.clear()
        #no clean way of getting locationMgr delete method to clean up the tree
        #since the tree is visible only to this model. Tried a pre-delete signal,
        #but that cannot carry arguments and so locationMgr cannot see the tree/key
        #to delete. Hence delete the key from here
        self.get_location().delete_key(vtree)
        self.delete()

    def lifetime(self):
        return self.table_lifetime

    def set_lifetime(self, time):
        self.life_time = time

    def distance_from(self, lat, lng):
        return 0

    def inc_numsitting(self):
        self.numSitting += 1
        self.save()

    def dec_numsitting(self):
        self.numSitting -= 1
        self.save()


class Membership(models.Model):
    date_created = models.DateTimeField()
    date_modified = models.DateTimeField()
    user = models.ForeignKey(User)
    table = models.ForeignKey(VirtualTable)


    def save(self, *args, **kwargs):
        if self.date_created == None:
            self.date_created = datetime.now()
        self.date_modified = datetime.now()
        super(Membership, self).save(*args, **kwargs)

def vtree_entry_timeout_handler(**kwargs):
    key_list = kwargs.pop('key_list')

    for key in key_list:
        wizlib.delete_key(key, vtree)

# Signal connections
virtualtable_vtree_timeout.connect(vtree_entry_timeout_handler, 
                                   dispatch_uid='wizcardship.models.wizcardship')

