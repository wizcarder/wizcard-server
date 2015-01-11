from lib.timer import Timer
from celery import task
from celery.contrib import rdb
from periodic.models import Periodic, PeriodicManager
from location_mgr.models import LocationMgr
from location_mgr.signals import location_timeout
from location_service.client import LocationServiceClient
import logging

logger = logging.getLogger(__name__)
@task
def tick():
    logger.debug('Timer Tick received')
    tsc = LocationServiceClient()
    tsc.print_trees(tree_type=None)
    e = Periodic.objects.get_expired()
    if e.count():
        logger.info('Expired objects found')
        ids = map(lambda x:  x.location.pk, e)
        location_timeout.send(sender=None, ids=ids)

    tsc.print_trees(tree_type=None)
