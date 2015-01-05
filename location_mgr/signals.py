from django.dispatch import Signal
location = Signal(providing_args=['lat', 'lng', 'tree_type'])
location_timeout = Signal(providing_args=['ids'])
