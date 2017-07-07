__author__ = 'aammundi'

from django.core.management.base import BaseCommand, CommandError
from wizcardship.models import Wizcard, ContactContainer
from userprofile.models import UserProfile
from wizcard import admin_wizcard_config
from django.utils import timezone
from media_mgr.signals import media_create
import pdb


now = timezone.now

class Command(BaseCommand):
    help = 'create wizcard from config dict'

    def handle(self, *args, **options):
        admin_user = UserProfile.objects.get_admin_user()
        if not admin_user:
            CommandError("please configure an admin user")

        admin_user.first_name = admin_wizcard_config.u['first_name']
        admin_user.last_name = admin_wizcard_config.u['last_name']
        admin_user.save()

        # create a Wizcard and attach to admin user
        wizcard, created = Wizcard.objects.get_or_create(
            user=admin_user,
            defaults=admin_wizcard_config.w
        )

        if not created:
            self.stdout.write('Existing WizCard found "%s". Updating...' % wizcard)

            for attr, value in admin_wizcard_config.w.iteritems():
                setattr(wizcard, attr, value)

            wizcard.save()

            cc = wizcard.contact_container.all()[0]
            for attr, value in admin_wizcard_config.cc.iteritems():
                setattr(cc, attr, value)
                cc.save()

            wizcard.media.all().delete()
            cc.media.all().delete()
        else:
            self.stdout.write('created new wizcard "%s"' % wizcard)
            # create cc
            cc = ContactContainer.objects.create(
                wizcard=wizcard,
                **admin_wizcard_config.cc
            )
            self.stdout.write('created new contact container "%s"' % cc)

        media_create.send(sender=wizcard, objs=admin_wizcard_config.wizcard_media)
        media_create.send(sender=cc, objs=admin_wizcard_config.cc_media)
