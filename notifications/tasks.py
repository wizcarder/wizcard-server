from celery import shared_task
from notifications.signals import notify

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
