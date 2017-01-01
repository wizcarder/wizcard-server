__author__ = 'aammundi'

from django.core.management.base import BaseCommand, CommandError
from wizcardship.models import Wizcard
from userprofile.models import UserProfile
from django.utils import timezone
from wizserver import verbs
from notifications import notify
import pdb

now = timezone.now


class Command(BaseCommand):
    help = 'connect admin wizcard to existing users. This should be run only Once'

    def handle(self, *args, **options):
        admin_user = UserProfile.objects.get_admin_user()
        if not admin_user:
            CommandError("please configure an admin user")

        # create a Wizcard and attach to admin user
        wizcard = admin_user.wizcard

        for w in Wizcard.objects.exclude(id=wizcard.id):
            # w(A)<-wizcard
            self.stdout.write('adding me->W(A) for "%s"' % w)
            Wizcard.objects.cardit(wizcard, w, status=verbs.ACCEPTED, cctx="")

            self.stdout.write('adding me(P)<-W for "%s"' % w)
            Wizcard.objects.cardit(w, wizcard, status=verbs.PENDING, cctx="")

            # notify w
            rel12 = wizcard.get_relationship(w)

            notify.send(
                wizcard.user, recipient=w.user,
                verb=verbs.WIZREQ_T[0],
                target=wizcard,
                action_object=rel12)