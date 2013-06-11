from django.dispatch import Signal
location = Signal(providing_args=['action_object', 'target', 'timestamp'])
location_timeout = Signal(providing_args=['ids'])
