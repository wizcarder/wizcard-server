import logging

from celery import task

from entity.models import Event


logger = logging.getLogger(__name__)
@task(ignore_result=True)
def expire():
    logger.debug('Timer Tick received')
    evids = Event.objects.expire()
    if evts:
        logger.info('Events expired found {%s}', ",".join(evids))


