import logging

from celery import task
from celery import shared_task
from notifications.signals import notify


logger = logging.getLogger(__name__)


from notifications.models import BaseNotification
from notifications.models import AsyncNotification
@task(ignore_result=True)
def async_handler():
    logger.debug('Messaging Tick received')

    notifs = AsyncNotification.objects.unread()



@shared_task(ignore_result=True)
def fanout_notifs(notif):
    users = notif.target.get_wizcard_users()

    for u in users:
        notify.send(
            notif.actor,
            recipient=u,
            notif_type=notif.notif_type,
            target=notif.target,
            action_object=notif.action_object,
            verb=notif.verb,
        )

    notif.mark_as_read()
