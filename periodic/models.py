from django.db import models
import datetime

TIMER_ONE_SHOT = 1
TIME_RECURRING = 2


class PeriodicManager(models.Manager):
    def get_expired(self):
        return self.objects.all()


class Periodic(models.Model):
    timeout_value = models.IntegerField(blank=False, null=False)
    expires_at = models.DateTimeField(default=datetime.datetime.now(), blank=False)
    timer_type = models.IntegerField(default=TIMER_ONE_SHOT)
    location = models.ForeignKey('location_mgr.LocationMgr', related_name="timer")

    objects = PeriodicManager()

    def start(self):
        self.expires_at = datetime.datetime.now() + datetime.timedelta(
                seconds=self.timeout_value)
        self.save()
