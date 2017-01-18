__author__ = 'aammundi'

import pdb
from location_service.tree_state_client import TreeStateClient

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Print Trees'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument('type', nargs='+', type=str)

    def handle(self, *args, **options):
        tree_type=options['type'] if 'type' in options else None

        tsc = TreeStateClient()
        tsc.print_trees(tree_type=tree_type)
