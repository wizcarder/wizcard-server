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
    notifs = AsyncNotification.objects.unread_notifs(delivery_mode=BaseNotification.DELIVERY_MODE_EMAIL)
    for n in notifs:
        n.mark_as_read()
        if n.delivery_mode == BaseNotification.DELIVERY_MODE_EMAIL:
            # emailer = HtmlGen(sender=n.actor, trigger=n.notif_type, target=n.target)
            # status = emailer.email_send()
            # n.update_status(status)
            pass


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
