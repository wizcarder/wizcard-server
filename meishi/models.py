from django.db import models
import heapq
from wizcardship.models import Wizcard

from django.utils import timezone

try:
    from django.utils import timezone
    now = timezone.now
except ImportError:
    now = datetime.datetime.now()

# Create your models here.
class Meishi(models.Model):
    wizcard = models.OneToOneField(Wizcard) 
    lat = models.DecimalField(null=True, max_digits=20, 
                              decimal_places=15, default=None)
    lng = models.DecimalField(null=True, max_digits=20, 
                              decimal_places=15, default=None)

    timestamp = models.DateTimeField(default=now)

    def __unicode__(self):
        ctx = {
            'lat': self.lat,
            'lng': self.lng,
            'timesince': self.timesince()
            }
        return '{%(lat) %(lng)} %(timesince)s ago' % ctx

    def timesince(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the
        current timestamp.
        """
        from django.utils.timesince import timesince as timesince_
        return timesince_(self.timestamp, now)

    def get_candidates(self):
        #filter those who are +- 10 seconds ?
        return self.objects.all()

    def distance_from(self, lat, lng):
        return wizlib.haversine(self.lng, self.lat, lng, lat)

    def satisfies_space_constraint(self, candidate):
        return True

    def check_meishi(self):
        #get candidates based on time. Then get (conditional) closest
        cl = self.get_candidates()

        h = []
        for h in cl:
            heapq.heapqpush(h, (h.distance_from(self.lat, self.lng), h.id))

        if not len(h):
            return None

        candidate = heapq.nsmallest(1, h)
        if self.satisfies_space_constraint(candidate):
            return candidate

        return None

