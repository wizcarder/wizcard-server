from django.dispatch import Signal
notify = Signal(
    providing_args=[
        'recipient', 'notif_type', 'do_push', 'action_object', 'target',  'description',
        'timestamp', 'start_date', 'end_date', 'delivery_mode', 'verb'
    ]
)
