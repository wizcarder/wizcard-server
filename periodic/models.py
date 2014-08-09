from django.db import models
from django.utils import timezone

TIMER_ONE_SHOT = 1
TIME_RECURRING = 2

class PeriodicManager(models.Manager):
    def get_expired(self):
        return self.filter(expires_at__lt = timezone.now())

    def clear_expired(self, e):
        map(lambda x: x.delete(), e)

class Periodic(models.Model):
    #timeout_value is in seconds
    timeout_value = models.IntegerField(blank=False, null=False)
    expires_at = models.DateTimeField(default=timezone.now, blank=False)
    timer_type = models.IntegerField(default=TIMER_ONE_SHOT)
    location = models.ForeignKey('location_mgr.LocationMgr', related_name="timer")

    objects = PeriodicManager()

    def __unicode__(self):
        return u'timeout: %s expires at: %s' % (self.timeout_value, self.expires_at)

    def start(self):
        self.expires_at = self.expires_at + timezone.timedelta(
                seconds=self.timeout_value)
        self.save()
	return self
