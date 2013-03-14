from django.dispatch import Signal
from lib import wizlib

virtualtable_vtree_timeout = Signal(providing_args=['key_list'])
