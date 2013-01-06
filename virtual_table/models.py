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
from wizserver import wizlib
from location_mgr.models import LocationMgr
from pytrie import SortedStringTrie as trie

vtree = trie()

class VirtualTableManager(models.Manager):
    def lookup(self, lat, lng, n):
        #AA:TODO: Is this the right "pythonic way" ?:w
        result, count =  VirtualTable.objects.lookup_by_lat_lng(tree=vtree, lat=lat, lng=lng, num_results=n)
        #convert result to query set result
        tables = map(lambda m: self.get(id=m), result)
        return tables, count


class VirtualTable(LocationMgr):
    tablename = models.CharField(max_length=40)
    numSitting = models.IntegerField(default=0, blank=True)
    secureTable = models.BooleanField(default=False)
    password = models.CharField(max_length=40, blank=True)
    creator = models.ForeignKey(User, related_name='tables')
    users = models.ManyToManyField(User, through='Membership')

    default_manager = VirtualTableManager()

    def __unicode__(self):
        return self.tablename

    def update_tree(self, *args, **kwargs):
        super(VirtualTable, self).update_tree(tree=vtree, *args, **kwargs)
        print 'updating to tree [{ptree}]'.format (ptree=vtree)

    def isSecure(self):
        return self.secureTable

    def table_exchange(self, joinee):
        joined = self.users.all().exclude(id=joinee.id)
        wizcard1 = User.objects.get(id=joinee.pk).wizcard

        wizcards = map(lambda u: User.objects.get(id=u.pk).wizcard, joined)
        implicit_exchange = self.isSecure()

        for wizcard2 in wizcards:
            wizlib.exchange(wizcard1, wizcard2, implicit_exchange)

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
        self.delete()

    def lifetime(self, time):
        return self.lifetime

    def set_lifetime(self, time):
        self.lifetime = time

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
