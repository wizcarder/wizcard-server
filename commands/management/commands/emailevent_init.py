__author__ = 'aammundi'

from email_and_push_infra.models import EmailEvent
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Initialize Email Events (ONLY ONCE)'

    def handle(self, *args, **options):
        if EmailEvent.objects.all().exists():
            self.stdout.write("Email Events already initialized")
            return

        # AA COmments: This doesn't need to be in dB. it can be in code as a
        # pre-filled list or dict etc
        for tevent in EmailEvent.EVENTS:
            if tevent[0] == EmailEvent.DIGEST:
                em = EmailEvent(event=tevent[0], event_type=EmailEvent.BUFFERED)
                em.save()
            else:
                em = EmailEvent(event=tevent[0])
                em.save()
