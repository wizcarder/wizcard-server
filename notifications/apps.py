from django.apps import AppConfig
from notifications.models import EmailEvent
class email_and_push_infraConfig(AppConfig):
    name = 'email_and_push_infra'
    verbose_name = "Email Push Infra"

    def ready(self):
        for evnt in EmailEvent.EVENTS:
            ev_type = EmailEvent.INSTANT
            if evnt[0] == EmailEvent.DIGEST:
                ev_type = EmailEvent.BUFFERED
            evt, created = EmailEvent.objects.get_or_create(event=evnt[0], event_type=ev_type)
            if created:
                evt.save()



