from django.dispatch import Signal
from lib import wizlib

wizcardship_accepted = Signal()


wizcardship_declined = Signal()


wizcardship_cancelled = Signal()



def create_wizcardship_instance(sender, instance, created, raw, **kwargs):
    from cards.models import Wizcard
    if created and not raw:
        Wizcard.objects.create(user=instance)


def create_userblocks_instance(sender, instance, created, raw, **kwargs):
    from cards.models import UserBlocks
    if created and not raw:
        UserBlocks.objects.create(user=instance)


def create_wizcardship_instance_post_syncdb(sender,
                                           app,
                                           created_models,
                                           verbosity,
                                           **kwargs):
    from django.contrib.auth.models import User
    from cards.models import Wizcard
    created = 0
    print "Creating wizcards"
    if User in created_models:
        for user in User.objects.filter(wizcardship__isnull=True):
            Wizcard.objects.create(user=user)
            created += 1
            if verbosity >= 2:
                print "Wizcard created for %s" % user
    if verbosity >= 1:
        print "%d wizcardships created" % created


def create_userblock_instance_post_syncdb(sender,
                                          app,
                                          created_models,
                                          verbosity,
                                          **kwargs):
    from django.contrib.auth.models import User
    from cards.models import UserBlocks
    created = 0
    print "Creating user blocks"
    if User in created_models:
        for user in User.objects.filter(user_blocks__isnull=True):
            UserBlocks.objects.create(user=user)
            created += 1
            if verbosity >= 2:
                print "User block created for %s" % user
    if verbosity >= 1:
        print "%d user blocks created" % created

