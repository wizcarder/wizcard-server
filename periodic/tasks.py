from lib.timer import Timer
from celery import task
from celery.contrib import rdb
from periodic.models import Periodic, PeriodicManager
from location_mgr.models import LocationMgr
from location_mgr.signals import location_timeout
import logging

logger = logging.getLogger(__name__)
@task
def process_timer(count=0):
    logger.debug('Timer Tick received')
    e = Periodic.objects.get_expired()
    if e.count():
        logger.info('Expired objects found')
        ids = map(lambda x:  x.location.pk, e)
        location_timeout.send(sender=None, ids=ids)
    Periodic.objects.clear_expired(e)
      
      
      
      
