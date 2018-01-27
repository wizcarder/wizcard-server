from django.dispatch import Signal
from notifications.models import BaseNotification, AsyncNotification, SyncNotification
from notifications.html_gen_methods import HtmlGen
from notifications.tasks import push_notification_to_app
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from datetime import timedelta


email_trigger = Signal(
    providing_args=[
        'source', 'trigger', 'target', 'to_email'
    ]
)

notify = Signal(
    providing_args=[
        'recipient', 'notif_type', 'do_push', 'action_object', 'target',  'description',
        'timestamp', 'start_date', 'end_date', 'delivery_mode', 'verb'
    ]
)


# Event based Triggers
TRIGGER_NEW_USER = 1
TRIGGER_PENDING_INVITE = 2
TRIGGER_CONNECTION_ACCEPTED = 3
TRIGGER_RECOMMENDATION_AVAILABLE = 4
TRIGGER_SCAN_CARD = 5

# Generic Triggers
TRIGGER_WEEKLY_DIGEST = 11


def email_trigger_handler(sender, **kwargs):
    trigger = kwargs.pop('trigger', None)
    sender = kwargs.pop('source')
    email = kwargs.pop('to_email', None)
    target = kwargs.pop('target', None)

    eap = AsyncNotification.objects.pushEvent(sender=sender, event=trigger, to=email, target=target)

    html = HtmlGen(sender, trigger, eap.get_to)
    html.run()
    eap.updateEmailTime(timezone.now)


def notify_handler(notif_type, **kwargs):
    """
    Handler function to create SyncNotification instance upon action signal call.
    """

    kwargs.pop('signal', None)
    recipient = kwargs.pop('recipient')
    actor = kwargs.pop('sender')
    delivery_mode = kwargs.pop('delivery_mode', BaseNotification.ALERT)
    delivery_type = kwargs.pop('delivery_type')
    verb = kwargs.pop('verb', "")
    target = kwargs.pop('target', None)
    action_object = kwargs.pop('action_object', None)
    action_object_content_type = ContentType.objects.get_for_model(action_object) if action_object else None
    action_object_object_id = action_object.pk if action_object else None
    do_push = kwargs.pop('do_push', False)
    start = kwargs.pop('start_date', timezone.now()+timedelta(minutes=1))
    end = kwargs.pop('end_date', start)

    """
    ASYNC goes in AsyncNotification. SYNC goes in SyncNotification
    """

    if delivery_type == BaseNotification.DELIVERY_TYPE_ASYNC:
        newnotify = AsyncNotification.objects.create(
            actor_content_type=ContentType.objects.get_for_model(actor),
            actor_object_id=actor.pk,
            recipient=recipient,
            target_content_type=ContentType.objects.get_for_model(target),
            target_object_id=target.pk,
            action_object_content_type=action_object_content_type,
            action_object_object_id=action_object_object_id,
            readed=False,
            delivery_mode=delivery_mode,
            notif_type=notif_type,
            verb=verb,
            timestamp=kwargs.pop('timestamp', timezone.now()),
            # AA: Comments: EmailPush cannot decide whether this is INSTANT or not.
            delivery_period=AsyncNotification.INSTANT,
            start_date=start,
            end_date=end,
            **kwargs
        )
    elif delivery_type == BaseNotification.DELIVERY_TYPE_SYNC:
        newnotify, created = SyncNotification.objects.get_or_create(
            actor_content_type=ContentType.objects.get_for_model(actor),
            actor_object_id=actor.pk,
            recipient=recipient,
            readed=False,
            notif_type=notif_type,
            verb=verb,
            target_content_type=ContentType.objects.get_for_model(target),
            target_object_id=target.pk,
            action_object_content_type=action_object_content_type,
            action_object_object_id=action_object_object_id,
            defaults={
                'public': bool(kwargs.pop('public', True)),
                'timestamp': kwargs.pop('timestamp', timezone.now()),
            }
        )

        # push a notification to app from here. Fire and forget
        if created:
            push_notification_to_app.delay(
                newnotify.actor_object_id,
                newnotify.recipient_id,
                newnotify.action_object_object_id,
                newnotify.action_object_content_type,
                newnotify.target_object_id,
                newnotify.target_content_type,
                newnotify.verb
            )
    else:
        raise AssertionError("Invalid delivery type %s" % delivery_type)

    return newnotify

email_trigger.connect(email_trigger_handler, dispatch_uid='notifications.models.AsyncNotification')
notify.connect(notify_handler, dispatch_uid='notifications.models.SyncNotification')
