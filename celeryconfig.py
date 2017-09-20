
from __future__ import absolute_import

import os

RUNENV = os.getenv('WIZRUNENV', 'dev')

APP_MAJOR = 1
APP_MINOR = 6

CELERY_RESULT_BACKEND = 'rpc'
from rabbit_service import rconfig
BROKER_URL = rconfig.AMPQ_DEFAULT_URL

EMAIL_TEMPLATE = '/invites/email_templatev4.png'
EMAIL_FROM_ADDR = 'wizcarder@getwizcard.com'

OCR_QUEUE_NAME = 'ocr'
PUSHNOTIF_QUEUE_NAME = 'pushnotif'
CELERY_DEFAULT_QUEUE = 'default'
CELERY_BEAT_QUEUE_NAME = 'beat'
IMAGE_UPLOAD_QUEUE_NAME = 'image_upload'
RECO_QUEUE_NAME = 'reco'


CELERY_ROUTES = {
    'lib.ocr.run_ocr': {'queue': OCR_QUEUE_NAME},
    'notifications.tasks.pushNotificationToApp': {'queue': PUSHNOTIF_QUEUE_NAME},
    'periodic.tasks.tick': {'queue': CELERY_DEFAULT_QUEUE},
    'queued_storage.tasks.Transfer': {'queue': IMAGE_UPLOAD_QUEUE_NAME},
    'queued_storage.tasks.TransferAndDelete': {'queue': IMAGE_UPLOAD_QUEUE_NAME},
    'wizcard.celery.debug_task': {'queue': CELERY_DEFAULT_QUEUE},
}

CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']

from datetime import timedelta
CELERYBEAT_SCHEDULE = {
    'tick': {
        'task': 'periodic.tasks.tick',
        'schedule': timedelta(seconds=60),
#       'options': {'queue': CELERY_BEAT_QUEUE_NAME}
    },
    'expire_events' : {
        'task' : 'events.task.expire',
        'schedule' : timedelta(seconds=86400),
    }
}
