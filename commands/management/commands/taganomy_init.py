__author__ = 'aammundi'

from taganomy.models import Taganomy

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Initialize Taganomy Defaults'

    def handle(self, *args, **options):
        from userprofile.models import UserProfile

        try:
            Taganomy.objects.get_default_category()
            self.stdout.write("Default already exists")
        except:
            try:
                Taganomy.objects.create(category="Others", editor=UserProfile.objects.get_admin_user())
            except:
                self.stdout.write("Problem Creating the Default Taganomy entry, check users")

