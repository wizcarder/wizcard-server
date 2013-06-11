from lib.timer import Timer
from celery import task
from celery.contrib import rdb
from periodic.models import PeriodicManager
from location_mgr.signals import location_timeout
@task
def process_timer(count=0):
    print 'Timer Tick received'
    e = PeriodicManager.objects.get_expired()
    ids = map(lambda x:  x.location.pk, e)
    location_timeout.send(ids=ids)
      
      
      
      
