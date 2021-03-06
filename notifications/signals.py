from django.dispatch import Signal

notify = Signal(
    providing_args=[
        'recipient', 'action_object', 'target',  'description', 'force_sync',
        'timestamp', 'start_date', 'end_date', 'notif_tuple', 'notif_operation', 'verb', 'notification_text',
        'action_object_object_id', 'action_object_content_type'
    ]
)
