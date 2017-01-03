__author__ = 'aammundi'

from django.core.management.base import BaseCommand
from wizcardship.models import Wizcard
from userprofile.models import UserProfile
from django.utils import timezone
from wizserver import verbs

now = timezone.now


class Command(BaseCommand):
    help = 'connect admin wizcard to existing users. This should be run only Once'

    def handle(self, *args, **options):
        wizcard = UserProfile.objects.get_admin_user().wizcard

        for w in wizcard.get_connected_to(verbs.ACCEPTED):
            Wizcard.objects.update_wizconnection(wizcard, w, half=False)