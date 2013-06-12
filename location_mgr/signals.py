from django.dispatch import Signal
location = Signal(providing_args=['lat', 'lng', 'key', 'tree_type'])
location_timeout = Signal(providing_args=['ids'])
