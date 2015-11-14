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
from notifications.models import notify
from base.cctx import ConnectionContext
from django.conf import settings
from django.utils import timezone

class VirtualTableManager(models.Manager):
    tag = None

    def set_tag(self, tag):
        self.tag = tag

    def lookup(self, cache_key, lat, lng, n, count_only=False):
        tables = None
        result, count = LocationMgr.objects.lookup(
                            cache_key,
                            "VTREE",
                            lat,
                            lng,
                            n)
        #convert result to query set result
        if count and not count_only:
            tables = map(lambda m: self.get(id=m), result)
        return tables, count

    def user_tables(self, user):
        return user.virtualtable_set.exclude(expired=True)

    #AA: TODO : get some max limit on this
    def query_tables(self, name):
        tables = self.filter(Q(tablename__istartswith=name) &
                Q(expired=False)) \
                [0: settings.DEFAULT_MAX_LOOKUP_RESULTS]
        return tables, tables.count()

    def serialize(self, tables, template):
        return serialize(tables, **template)

    def serialize_split(self, tables, user, template):
        created, joined, connected, others = self.split_table(tables, user)

        s = dict()
        if created:
            s['created'] = self.serialize(created, template)
        if joined:
            s['joined'] = self.serialize(joined, template)
        if connected:
            s['connected'] = self.serialize(connected, template)
        if others:
            s['others'] = self.serialize(others, template)
        return s

    def split_table(self, tables, user):
        created = []
        joined = []
        connected = []
        others = []
        for t in tables:
            if t.is_creator(user):
                created.append(t)
            elif t.is_member(user):
                joined.append(t)
            elif Wizcard.objects.are_wizconnections(
                    user.wizcard,
                    t.creator.wizcard):
                connected.append(t)
            else:
                others.append(t)
        return created, joined, connected, others


class VirtualTable(models.Model):
    tablename = models.CharField(max_length=40)
    numSitting = models.IntegerField(default=0, blank=True)
    secureTable = models.BooleanField(default=False)
    password = models.CharField(max_length=40, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    a_created = models.CharField(max_length=40, blank=True)
    creator = models.ForeignKey(User, related_name='tables')
    timeout = models.IntegerField(default=30)
    expired = models.BooleanField(default=False)
    users = models.ManyToManyField(User, through='Membership')
    location = generic.GenericRelation(LocationMgr)

    objects = VirtualTableManager()

    def __unicode__(self):
        return self.tablename

    def serialize(self, template):
        return serialize(self, **template)

    def create_location(self, lat, lng):
        location.send(
                sender=self,
                lat=lat,
                lng=lng,
                tree="VTREE")

    def is_secure(self):
        return self.secureTable

    def get_member_wizcards(self):
        members = map(lambda u: u.wizcard, self.users.all().exclude(id=self.creator.id))
        return serialize(members, **fields.wizcard_template_brief)

    def get_creator(self):
        return serialize(self.creator.wizcard, **fields.wizcard_template_brief)

    def table_exchange(self, joinee):
        joined = self.users.all().exclude(id=joinee.id)
        wizcard1 = User.objects.get(id=joinee.pk).wizcard

        wizcards = map(lambda u: u.wizcard, joined)
        implicit_exchange = self.is_secure()

        for wizcard2 in wizcards:
            cctx = ConnectionContext(asset_obj=self)
            Wizcard.objects.exchange(wizcard1, wizcard2, cctx)

        return self

    def name(self):
        return self.tablename

    def is_member(self, user):
        return bool(self.users.filter(id=user.id).exists())

    def is_creator(self, user):
        return bool(self.creator == user)

    def join_table_and_exchange(self, user, password, skip_password=False):
        #check password
        if (not self.is_secure()) or \
            (self.password == password) or skip_password:
            m, created = Membership.objects.get_or_create(user=user, table=self)
            if not created:
                #somehow already a member
		        return self
            self.inc_numsitting()

            #send notif to all existing joinees, to update table counts
            for u in self.users.exclude(id=user.id):
                notify.send(
                    user,
                    recipient=u,
                    verb=verbs.WIZCARD_TABLE_JOIN[0],
                    target=self
                )

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
        #send notif to all members, just like join
        for u in self.users.exclude(id=user.id):
            notify.send(
                user,
                recipient=u,
                verb=verbs.WIZCARD_TABLE_LEAVE[0],
                target=self
            )

        return self

    def delete(self, *args, **kwargs):
        #notify members of deletion (including self)
        verb = kwargs.pop('type', verbs.WIZCARD_TABLE_DESTROY[0])
        members = self.users.all()
        for member in members:
            notify.send(
                self.creator,
                recipient=member,
                verb=verb,
                target=self)

        self.location.get().delete()

        if verb == verbs.WIZCARD_TABLE_TIMEOUT[0]:
            self.expired = True
            self.save()
        else:
            self.users.clear()
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
        if not self.expired:
            return self.location.get().timer.get().time_remaining()
        return 0

class Membership(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User)
    table = models.ForeignKey(VirtualTable)


    def save(self, *args, **kwargs):
        super(Membership, self).save(*args, **kwargs)
