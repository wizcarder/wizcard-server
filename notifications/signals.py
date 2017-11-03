from django.dispatch import Signal
notify = Signal(providing_args=['recipient', 'actor', 'verb', 'action_object', 'target', 'is_offline'
    'description', 'timestamp','onlypush'])
