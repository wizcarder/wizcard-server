__author__ = 'aammundi'

from django.core.management.base import BaseCommand, CommandError
from userprofile.models import UserProfile
from django.utils import timezone
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


now = timezone.now


class Command(BaseCommand):
    help = 'create portal user and setup auth-token for it'

    def handle(self, *args, **options):
        u = UserProfile.objects.get_portal_user_internal()
        if u:
            self.stdout.write('Existing portal user found "%s" ' % u.user.username)

            # see if token exists
            if hasattr(u.user, 'auth_token'):
                self.stdout.write('Token Exists "%s" ' % u.user.auth_token)
            else:
                self.stdout.write('creating Token for Portal User "%s"' % u.user.username)
                t = Token.objects.create(user=u.user)
                self.stdout.write('created Token: "%s"' % t)
        else:
            # create portal user
            username = raw_input('Enter username: ')
            password = raw_input('Enter Password')
            u = User.objects.create(username=username, password=password)
            u.profile.create_user_type_instance(UserProfile.PORTAL_USER_INTERNAL)
            t = Token.objects.create(user=u)
            self.stdout.write('created Token: "%s"' % t)
