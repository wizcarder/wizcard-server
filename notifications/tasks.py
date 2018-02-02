import logging

from celery import task
from notifications.models import AsyncNotification
from wizserver.response import AsyncNotifResponse

logger = logging.getLogger(__name__)

@task(ignore_result=True)
def async_handler():
    logger.debug('Messaging Tick received')

    notifs = AsyncNotification.objects.unread()

    AsyncNotifResponse(notifs)

