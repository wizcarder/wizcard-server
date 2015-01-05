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
from wizserver import fields, verbs
from virtual_table.signals import virtualtable_vtree_timeout
from notifications.models import notify, Notification
from django.conf import settings
from django.utils import timezone

class VirtualTableManager(models.Manager):
    tag = None

    def set_tag(self, tag):
        self.tag = tag

    def lookup(self, lat, lng, n, count_only=False):
        tables = None
        result, count = LocationMgr.objects.lookup(
                            "VTREE",
                            lat,
                            lng,
                            n)
        #convert result to query set result
        if count and not count_only:
            tables = map(lambda m: self.get(id=m), result)
        return tables, count

    #AA: TODO : get some max limit on this
    def query_tables(self, name):
        tables = self.filter(Q(tablename__istartswith=name)) \
                [0: settings.DEFAULT_MAX_LOOKUP_RESULTS]
        return tables, tables.count()

    def serialize(self, tables, merge=False):
        template = fields.table_merged_template if merge else \
                fields.table_template
        return serialize(tables, **template)

    def serialize_split(self, tables, user, merge=False, flatten=False):

        s = None
        created, joined, others = self.split_table(tables, user)

        if flatten:
            s = []
            if created:
                self.set_tag("created")
                s += self.serialize(created, merge)
            if joined:
                self.set_tag("joined")
                s += self.serialize(joined, merge)
            if others:
                self.set_tag("others")
                s += self.serialize(others, merge)
            self.set_tag(None)
        else:
            s = dict()
            if created:
                s['created'] = self.serialize(created, merge)
            if joined:
                s['joined'] = self.serialize(joined, merge)
            if others:
                s['others'] = self.serialize(others, merge)

        return s

    def split_table(self, tables, user):
        created = []
        joined = []
        others = []
        for t in tables:
            if t.is_creator(user):
                created.append(t)
            elif t.is_member(user):
                joined.append(t)
            else:
                others.append(t) 
        return created, joined, others


class VirtualTable(models.Model):
    tablename = models.CharField(max_length=40)
    numSitting = models.IntegerField(default=0, blank=True)
    secureTable = models.BooleanField(default=False)
    password = models.CharField(max_length=40, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    a_created = models.CharField(max_length=40, blank=True)
    creator = models.ForeignKey(User, related_name='tables')
    timeout = models.IntegerField(default=30)
    users = models.ManyToManyField(User, through='Membership')
    location = generic.GenericRelation(LocationMgr)

    objects = VirtualTableManager()

    def __unicode__(self):
        return self.tablename

    def create_location(self, lat, lng):
        location.send(
                sender=self, 
                lat=lat, 
                lng=lng, 
                tree="VTREE")

    def is_secure(self):
        return self.secureTable

    def table_exchange(self, joinee):
        joined = self.users.all().exclude(id=joinee.id)
        wizcard1 = User.objects.get(id=joinee.pk).wizcard

        wizcards = map(lambda u: User.objects.get(id=u.pk).wizcard, joined)
        implicit_exchange = self.is_secure()

        for wizcard2 in wizcards:
            Wizcard.objects.exchange(wizcard1, wizcard2, 
                    implicit_exchange, table=self)

        return self

    def name(self):
        return self.tablename

    def is_member(self, user):
        return bool(self.users.filter(id=user.id).exists())

    def is_creator(self, user):
        return bool(self.creator == user)

    def join_table_and_exchange(self, user, password, do_exchange):
        #check password
        if not self.is_secure() or self.password == password:
            m, created = Membership.objects.get_or_create(user=user, table=self)
	    if not created:
		#somehow already a member
		return self
	    self.inc_numsitting()
            if do_exchange is True:
                self.table_exchange(user)
        else:
            return None
        return self

    def leave_table(self, user):
        try:
            user.membership_set.get(table=self).delete()
            self.dec_numsitting()
        except:
            pass

        return self

    def delete(self, *args, **kwargs):
	#notify members of deletion (including self)
	members = self.users.all()
        verb = kwargs.pop('type', verbs.WIZCARD_TABLE_DESTROY[0])
	for member in members:
	    notify.send(self.creator, recipient=member, verb = verb, target=self)
        self.users.clear()
        self.location.get().delete()
        super(VirtualTable, self).delete(*args, **kwargs)

    def distance_from(self, lat, lng):
        return 0

    def inc_numsitting(self):
        self.numSitting += 1
        self.save()

    def dec_numsitting(self):
        self.numSitting -= 1
        self.save()

    #some callables used by serializer
    def get_tag(self):
        return VirtualTable.objects.tag

    def time_remaining(self):
        r = timezone.timedelta(minutes=self.timeout) - \
                (timezone.now() - self.created)

        if (r.days < 0):
            return 0
        else: 
            return r.seconds

class Membership(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User)
    table = models.ForeignKey(VirtualTable)


    def save(self, *args, **kwargs):
        super(Membership, self).save(*args, **kwargs)

def vtree_entry_timeout_handler(**kwargs):
    key_list = kwargs.pop('key_list')

    for key in key_list:
        wizlib.ptree_delete(key, vtree)

# Signal connections
virtualtable_vtree_timeout.connect(vtree_entry_timeout_handler, 
                                   dispatch_uid='wizcardship.models.wizcardship')

