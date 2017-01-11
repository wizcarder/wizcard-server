__author__ = 'aammundi'

from django.core.management.base import BaseCommand, CommandError
from wizcardship.models import Wizcard, ContactContainer
from userprofile.models import UserProfile
from wizcard import admin_wizcard_config
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from lib import noembed
import pdb


now = timezone.now

class Command(BaseCommand):
    help = 'create wizcard from config dict'

    def handle(self, *args, **options):
        admin_user = UserProfile.objects.get_admin_user()
        if not admin_user:
            CommandError("please configure an admin user")

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
        else:
            self.stdout.write('created new wizcard "%s"' % wizcard)
            # create cc
            cc = ContactContainer.objects.create(
                wizcard=wizcard,
                **admin_wizcard_config.cc
            )
            self.stdout.write('created new contact container "%s"' % cc)

        # upload images
        # thumbnail
        self.stdout.write('uploading thumbmail')
        f = open(admin_wizcard_config.THUMBNAIL_IMAGE_PATH, 'rb')
        rawimage = f.read()
        upfile = SimpleUploadedFile("%s-%s.jpg" %
                                    (wizcard.pk, now().strftime("%Y-%m-%d %H:%M")),
                                    rawimage, "image/jpeg")
        wizcard.thumbnailImage.save(upfile.name, upfile)

        # video thumbnail url
        resp = noembed.embed(wizcard.videoUrl)
        wizcard.videoThumbnailUrl = resp.thumbnail_url

        wizcard.save()

        # bizcard image
        f = open(admin_wizcard_config.BIZCARD_IMAGE_PATH, 'rb')
        rawimage = f.read()
        upfile = SimpleUploadedFile("%s-%s.jpg" %
                                    (wizcard.pk, now().strftime("%Y-%m-%d %H:%M")),
                                    rawimage, "image/jpeg")
        cc.f_bizCardImage.save(upfile.name, upfile)

        self.stdout.write('Successfully created wizcard "%s"' % wizcard)