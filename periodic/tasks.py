from lib.timer import Timer
from celery import task
from celery.contrib import rdb
from periodic.models import Periodic, PeriodicManager
from location_mgr.models import LocationMgr
from location_mgr.signals import location_timeout
@task
def process_timer(count=0):
    print 'Timer Tick received'
    e = Periodic.objects.get_expired()
    ids = map(lambda x:  x.location.pk, e)
    location_timeout.send(sender=None, ids=ids)
      
      
      
      
