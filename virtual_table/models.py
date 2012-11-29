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

class VirtualTableManager(models.Manager):
    def get_closest_n(self, n, lat, lng):
        return self.all(), self.all().count()


class VirtualTable(models.Model):
    tablename = models.CharField(max_length=40)
    lat = models.FloatField()
    lng = models.FloatField()
    #centroid = models.BooleanField(default=False)
    numSitting = models.IntegerField(default=0, blank=True)
    secureTable = models.BooleanField(default=False)
    password = models.CharField(max_length=40, blank=True)
    creator = models.ForeignKey(User, related_name='tables')
    users = models.ManyToManyField(User, through='Membership')

    objects = VirtualTableManager()

    def __unicode__(self):
        return self.tablename

    def set_location(self, lat, lng):
        self.lat = lat
        self.lng = lng

    def isSecure(self):
        return self.secureTable
    

    def table_exchange(self, joinee):
        joined = self.users.all().exclude(id=joinee.id)
        wizcard1 = MyUser.objects.get(id=joinee.pk).default_wizcard(joinee)

        wizcards = map(lambda u: MyUser.objects.get(id=u.pk).default_wizcard(u), joined)
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


