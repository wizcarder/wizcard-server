from django.dispatch import Signal
from email_and_push_infra.models import EmailAndPush
from html_gen_methods import HtmlGen
from django.utils import timezone

email_trigger = Signal(providing_args=['wizcard', 'trigger', 'target', 'to_email'])

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
    wizcard = kwargs.pop('wizcard')
    email = kwargs.pop('to_email', None)
    target = kwargs.pop('target', None)


    eap, created = EmailAndPush.objects.get_or_create(wizcard=wizcard, event=trigger, target=target, to=email)

    html = HtmlGen(wizcard, trigger, target.email)
    html.run()
    eap.save()


email_trigger.connect(callback, dispatch_uid='email_and_push_infra.models.EmailAndPush')
