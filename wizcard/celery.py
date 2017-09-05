from __future__ import absolute_import

import os

from celery import Celery
from raven import Client
from raven.contrib.celery import register_signal

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wizcard.settings')

from django.conf import settings

wizcard_app = Celery('wizcard')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
wizcard_app.config_from_object('celeryconfig')
wizcard_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS + ("lib.ocr", "lib.create_share"))



# Celery signal registration
if hasattr(settings, 'RAVEN_CONFIG'):
        client = Client(dsn=settings.RAVEN_CONFIG['dsn'])
        register_signal(client)

@wizcard_app.task(bind=True)
def debug_task(self):
        print('Request: {0!r}'.format(self.request))
