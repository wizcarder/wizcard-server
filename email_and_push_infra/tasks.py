import logging

from celery import task

from email_and_push_infra.models import EmailAndPush
from email_and_push_infra.html_gen_methods import HtmlGen
from notifications.models import Notification
from notifications.tasks import ApnsMsg


logger = logging.getLogger(__name__)


@task(ignore_result=True)
def message_event_handler():
    logger.debug('Messaging Tick received')
    notifs = Notification.objects.offline()

    for n in notifs:
        email_and_push = n.action_object
        if email_and_push.delivery == EmailAndPush.EMAIL:
            emailer = HtmlGen(sender=n.actor, trigger=n.verb, target=n.target)
            emailer.run()
        elif email_and_push.delivery == EmailAndPush.EMAIL:
         # Need a wrapper around ApnsMsg
            pass


