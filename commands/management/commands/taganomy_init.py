__author__ = 'aammundi'

import pdb
from taganomy.models import Taganomy
from django.contrib.auth.models import User

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Initialize Taganomy Defaults'

    def handle(self, *args, **options):
        try:
            default_cat = Taganomy.objects.get(id=10)
            self.stdout.write("Default already exists")
        except:
            try:
                dcat = Taganomy(category="Others", editor=User.objects.all()[0])
                dcat.id = 10
                dcat.save()
            except:
                self.stdout.write("Problem Creating the Default Taganomy entry, check users")

