from django.db import models
import heapq
from wizcardship.models import Wizcard
from lib import wizlib
import pdb

from django.utils import timezone

try:
    from django.utils import timezone
    now = timezone.now
except ImportError:
    now = datetime.datetime.now()

class MeishiMgr(models.Manager):
    def get_candidates(self, m):
        #filter those who are +- 10 seconds ?
        return self.exclude(wizcard=m.wizcard)

    def pair_up(self, meishi1, meishi2):
        meishi1.pairs.add(meishi2)

    def unpair(self, meishi1, meishi2):
        meishi1.pairs.remove(meishi2)

# Create your models here.A

class Meishi(models.Model):
    wizcard = models.ForeignKey(Wizcard) 
    lat = models.DecimalField(max_digits=20, decimal_places=15)
    lng = models.DecimalField(max_digits=20, decimal_places=15)
    timestamp = models.DateTimeField(default=now)
    pairs = models.ManyToManyField('self', symmetrical=True, blank=True)
    #self referential 1:1

    objects = MeishiMgr()

    def __unicode__(self):
        ctx = {
            'lat': self.lat,
            'lng': self.lng,
            'timesince': self.timesince()
            }
        return '{%(lat)s, %(lng)s} %(timesince)s ago' % ctx

    def timesince(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the
        current timestamp.
        """
        from django.utils.timesince import timesince as timesince_
        return timesince_(self.timestamp, now)

    def distance_from(self, lat, lng):
        return wizlib.haversine(self.lng, self.lat, lng, lat)

    def satisfies_space_constraint(self, candidate):
        return True

    def check_meishi(self):
        #first check if already paired
 
        #get candidates based on time. Then get (conditional) closest
        cl = Meishi.objects.get_candidates(self)

        h = []
        for c in cl:
            heapq.heappush(h, (c.distance_from(self.lat, self.lng), c))

        if not len(h):
            return None

        candidate = heapq.nsmallest(1, h)[0][1]
        if self.satisfies_space_constraint(candidate):
            MeishiPairs.objects.create(m_first=self,
                                       m_second=candidate)
            return candidate

        return None
