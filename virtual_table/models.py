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

class VirtualTableManager(models.Manager):
    def get_closest_n(self, n, lat, lng):
        return self.all(), self.all().count()


class VirtualTable(models.Model):
    tablename = models.CharField(max_length=40)
    lat = models.FloatField()
    lng = models.FloatField()
    #centroid = models.FloatField(null=True, blank=True)
    numSitting = models.IntegerField(null=True, blank=True)
    isSecure = models.BooleanField(default=False)
    password = models.CharField(max_length=40, blank=True)
    creator = models.ForeignKey(User, related_name='tables')
    users = models.ManyToManyField(User, through='Membership')

    objects = VirtualTableManager()

    def __unicode__(self):
        return self.name

    def set_location(self, lat, lng):
        self.lat = lat
        self.lng = lng

    def exchange(self, joinee):
        return self

    def name(self):
        return self.name

    def join_table(self, user):
        m, created = Membership.objects.get_or_create(user=user, table=self)
        return self

    def leave_table(self, user):
        self.users.remove(user)
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

