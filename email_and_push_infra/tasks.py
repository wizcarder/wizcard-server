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
        n.mark_as_read()
        if delivery_type == Notification.EMAIL:
            # AR: TODO: Disabling email for girnar - Remember to enable it later
            return
            #emailer = HtmlGen(sender=n.actor, trigger=n.notif_type, target=n.target)
            #status = emailer.email_send()
            #n.update_status(status)
        elif delivery_type == Notification.PUSHNOTIF:
            pushNotificationToApp.delay(n.actor_object_id,
                                        n.recipient.id,
                                        n.action_object_object_id,
                                        n.action_object_content_type,
                                        n.target_object_id,
                                        n.target_content_type,
                                        n.notif_type,
                                        n.verb
                                        )




