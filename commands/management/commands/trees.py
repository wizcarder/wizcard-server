__author__ = 'aammundi'

from location_service.tree_state_client import TreeStateClient

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    args = '<tree_type>'
    help = 'Print Trees'

    def handle(self, *args, **options):
        tsc = TreeStateClient()
        if not args:
            print tsc.print_trees(tree_type=None)
        else:
            for ttype in args:
                print tsc.print_trees(tree_type=ttype)