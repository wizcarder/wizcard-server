import logging

from celery import task

from periodic.models import Periodic
from location_mgr.signals import location_timeout
from location_service.tree_state_client import TreeStateClient

logger = logging.getLogger(__name__)
@task(ignore_result=True)
def tick():
    logger.debug('Timer Tick received')
    tsc = TreeStateClient()

    e = Periodic.objects.get_expired()
    if e.count():
        ids = map(lambda x:  x.location.pk, e)
        logger.info('Expired objects found {%s}', ids)
        location_timeout.send(sender=None, ids=ids)

    tsc.print_trees(tree_type=None)
