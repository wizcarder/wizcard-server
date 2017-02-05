from django.dispatch import Signal
from email_and_push_infra.models import EmailAndPush
from html_gen_methods import HtmlGen

email_trigger = Signal(providing_args=['wizcard', 'trigger'])

# Event based Triggers
TRIGGER_NEW_USER = 1
TRIGGER_PENDING_INVITE = 2
TRIGGER_CONNECTION_ACCEPTED = 3
TRIGGER_RECOMMENDATION_AVAILABLE = 4

# Generic Triggers
TRIGGER_WEEKLY_DIGEST = 11



def callback(sender, **kwargs):
    trigger = kwargs.pop('trigger', None)
    wizcard = kwargs.pop('wizcard')

    eap = EmailAndPush.objects.get_or_create(wizcard=wizcard)

    if trigger == TRIGGER_NEW_USER:
        eap.onboarding_sent = True
        eap.save()

    html = HtmlGen(wizcard, trigger)
    html.run()


email_trigger.connect(callback, dispatch_uid='email_and_push_infra.models.EmailAndPush')