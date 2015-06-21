from django.db import models
import heapq
from wizcardship.models import Wizcard
from notifications.models import Notification
from lib import wizlib
from datetime import timedelta
from django.core.cache import cache
import pdb

from django.utils import timezone

try:
    from django.utils import timezone
    now = timezone.now
except ImportError:
    now = datetime.datetime.now()

MEISHI_TIME_THRESHOLD = 10

#TODO: Need to see whether lat, lng granularity can be increased
MEISHI_DIST_THRESHOLD = 200.00

class MeishiMgr(models.Manager):

    # Time interval between 2 gestures in seconds

    def get_candidates(self, m):
        #filter those who are +- 10 seconds ?
        qs1 = self.exclude(wizcard=m.wizcard).order_by('-timestamp')
        delta = timedelta(seconds=MEISHI_TIME_THRESHOLD)
        end_time = m.timestamp + delta
        start_time = m.timestamp - delta

        qs2 = qs1.filter(timestamp__range = (start_time, end_time))
        return qs2, qs2.count()

    def pair_up(self, meishi1, meishi2):
        meishi1.pairs.add(meishi2)

    def unpair(self, meishi1, meishi2):
        meishi1.pairs.remove(meishi2)

#AA:Comments: might be good to have an "active" kind of field tracking
#which meishi's ae active. get_candidates can exclude inactive meishi's.
#it's active when the record is created...maybe marked inactive/complete
#when paired up...will have to figure out additional ways of inactivating
#maybe this is one use-case for sending meishi_end
#in general, instead if binary state, it could be multiple states [active, paired, complete, didnt_find_pair]..etc

class Meishi(models.Model):
    wizcard = models.ForeignKey(Wizcard, related_name="meishis")
    lat = models.DecimalField(max_digits=20, decimal_places=15)
    lng = models.DecimalField(max_digits=20, decimal_places=15)
    timestamp = models.DateTimeField(default=now)
    #self referential 1:1
    pairs = models.ManyToManyField('self', symmetrical=True, blank=True)

    objects = MeishiMgr()

    def __unicode__(self):
        ctx = {
            'lat': self.lat,
            'lng': self.lng,
            'timesince': self.timesince()
            }
        return '{%(lat)s, %(lng)s} %(timesince)s ago' % ctx

    def timesince(self, _now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the
        current timestamp.
        """
        from django.utils.timesince import timesince as timesince_
        return timesince_(self.timestamp, _now)

    def distance_from(self, lat, lng):
        return wizlib.haversine(self.lng, self.lat, lng, lat)

    def satisfies_space_constraint(self, candidate):
        return True
        meishi_distance = self.distance_from(candidate.lat,candidate.lng)
        if meishi_distance <= MEISHI_DIST_THRESHOLD:
            return True
        return False

    def check_meishi(self):
        #first check if already paired
        if self.pairs.exists():
            return self.pairs.get()

        #get candidates based on time. Then get (conditional) closest
        cl, count = Meishi.objects.get_candidates(self)
        if not count:
            return None

        h = []
        for c in cl:
            heapq.heappush(h, (c.distance_from(self.lat, self.lng), c))

        candidate = heapq.nsmallest(1, h)[0][1]
        if self.satisfies_space_constraint(candidate):
            Meishi.objects.pair_up(self,candidate)
            #AA: Where is this cached wizcard being used ?
            #you might want to use this for when the candidate comes
            #in...in which case the key should probably be candidate wizcard_id
            cache.set(self.wizcard.id, candidate.wizcard)
            return candidate

        return None