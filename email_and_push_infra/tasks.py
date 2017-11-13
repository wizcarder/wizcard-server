import logging

from celery import task

from email_and_push_infra.models import EmailAndPush
from email_and_push_infra.html_gen_methods import HtmlGen
from notifications.models import Notification
from notifications.tasks import pushNotificationToApp


logger = logging.getLogger(__name__)


@task(ignore_result=True)
def message_event_handler():
    logger.debug('Messaging Tick received')
    notifs = Notification.objects.get_async()

    for n in notifs:
        delivery_type = n.delivery_type
        if delivery_type == Notification.EMAIL:
            emailer = HtmlGen(sender=n.actor, trigger=n.notif_type, target=n.target)
            status = emailer.email_send()
            n.update_status(status)
        elif delivery_type == Notification.PUSHNOTIF:
            wizcard_users = n.target.get_wizcard_users()
            for wusr in wizcard_users:
                pushNotificationToApp.delay(n.actor_object_id,
                                            wusr.id,
                                            n.action_object_object_id,
                                            n.action_object_content_type,
                                            n.target_object_id,
                                            n.target_content_type,
                                            n.notif_type,
                                            n.verb
                                            )
        n.mark_as_read()



