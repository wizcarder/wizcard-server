
from __future__ import absolute_import
import os

RUNENV = os.getenv('WIZRUNENV', 'dev')

APP_MAJOR = 1
APP_MINOR = 6

result_backend = 'rpc'
from rabbit_service import rconfig

task_serializer = 'pickle'
broker_url = rconfig.AMPQ_DEFAULT_URL

email_template = '/invites/email_templatev4.png'
email_from_addr = 'wizcarder@getwizcard.com'

ocr_queue_name = 'ocr'
pushnotif_queue_name = 'pushnotif'
celery_default_queue = 'default'
celery_beat_queue_name = 'beat'
image_upload_queue_name = 'image_upload'
reco_queue_name = 'reco'


task_routes = {
    'lib.ocr.run_ocr': {'queue': ocr_queue_name},
    'notifications.push_tasks.push_notification_to_app': {'queue': pushnotif_queue_name},
    'periodic.tasks.tick': {'queue': celery_beat_queue_name},
    'queued_storage.tasks.Transfer': {'queue': image_upload_queue_name},
    'queued_storage.tasks.TransferAndDelete': {'queue': image_upload_queue_name},
    'wizcard.celery.debug_task': {'queue': celery_default_queue},
    'notifications.tasks.async_handler': {'queue': celery_beat_queue_name},
    'entity.tasks.expire': {'queue': celery_beat_queue_name}
}

accept_content = ['pickle', 'json']

from datetime import timedelta

beat_schedule = {
    'tick': {
        'task': 'periodic.tasks.tick',
        'schedule': timedelta(seconds=60),
        'options': {'queue': celery_beat_queue_name}
    },
    'expire_events': {
        'task': 'entity.tasks.expire',
        'schedule': timedelta(seconds=86400),
        'options': {'queue': celery_beat_queue_name}
    },
    'async_handler': {
        'task': 'notifications.tasks.async_handler',
        'schedule': timedelta(seconds=60),
        'options': {'queue': celery_beat_queue_name}
    }
}
