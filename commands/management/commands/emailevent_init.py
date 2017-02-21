__author__ = 'aammundi'

import pdb
from email_and_push_infra.models import EmailEvent

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Initialize Email Events (ONLY ONCE)'

    def handle(self, *args, **options):
        email_events = EmailEvent.objects.all()
        if email_events:
            self.stdout.write("Email Events already initialized")
        else:
            for tevent in EmailEvent.EVENTS:
                if tevent[0] == EmailEvent.DIGEST:
                    em = EmailEvent(event=tevent[0], event_type=EmailEvent.BUFFERED)
                    em.save()
                else:
                    em = EmailEvent(event=tevent[0])
                    em.save()
