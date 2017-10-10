import logging

from celery import task

from entity.models import Event


logger = logging.getLogger(__name__)
@task(ignore_result=True)
def expire():
    logger.debug('Event Tick received')
    e = Event.objects.get_expired()
    for _e in e:
        logger.info('Expiring event {%s}', _e)
        _e.expire()


