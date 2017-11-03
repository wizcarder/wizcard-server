from django.dispatch import Signal
from email_and_push_infra.models import EmailAndPush
from email_and_push_infra.models import EmailAndPushManager
from html_gen_methods import HtmlGen
from django.utils import timezone
import pdb

message_trigger = Signal(providing_args=['source', 'trigger', 'target', 'delivery'])

# Event based Triggers
TRIGGER_NEW_USER = 1
TRIGGER_PENDING_INVITE = 2
TRIGGER_CONNECTION_ACCEPTED = 3
TRIGGER_RECOMMENDATION_AVAILABLE = 4
TRIGGER_SCAN_CARD = 5

# Generic Triggers
TRIGGER_WEEKLY_DIGEST = 11


def callback(sender, **kwargs):
    trigger = kwargs.pop('trigger', None)
    sender = kwargs.pop('source')
    delivery = kwargs.pop('delivery')
    target = kwargs.pop('target', None)

    eap = EmailAndPush.objects.pushEvent(sender=sender,event=trigger, delivery=delivery, target=target)




message_trigger.connect(callback, dispatch_uid='email_and_push_infra.models.EmailAndPush')
