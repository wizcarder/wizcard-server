from django.db import models
from django.utils import timezone
import pdb

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
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=timezone.now, blank=False)
    timer_type = models.IntegerField(default=TIMER_ONE_SHOT)
    location = models.ForeignKey('location_mgr.LocationMgr', related_name="timer")

    objects = PeriodicManager()

    def __unicode__(self):
        return u'timeout: %s expires in: %ss (%sm)' % (self.timeout_value, \
                self.time_remaining(), self.time_remaining()/60)

    #returns in seconds
    def time_remaining(self):
        r = self.expires_at - timezone.now()
        if (r.days < 0):
            return 0
        else:
            return r.seconds

    #starts timer based on created_at as epoch
    def start(self):
        self.expires_at = self.created_at + timezone.timedelta(
                seconds=self.timeout_value)
        self.save()
        return self

    #starts timer based on now as epoch
    def restart(self, t=None):
        if t:
            self.timeout_value = t
        self.expires_at = timezone.now() + timezone.timedelta(
                seconds=self.timeout_value)
        self.save()
        return self
    
    #sets new timeout and restarts timer
    def extend_timer(self, e_timeout):
        self.timeout_value = e_timeout + self.time_remaining()
        self.restart()
        self.save()
        return self

