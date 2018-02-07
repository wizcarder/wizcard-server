from django.dispatch import Signal

notify = Signal(
    providing_args=[
        'recipient', 'action_object', 'target',  'description', 'force_sync',
        'timestamp', 'start_date', 'end_date', 'delivery_mode', 'notif_tuple'
    ]
)
