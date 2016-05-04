from __future__ import absolute_import

import os

from celery import Celery
from kombu import Consumer, Exchange, Queue

from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wizcard.settings')

wizcard_app = Celery('wizcard')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
wizcard_app.config_from_object('django.conf:settings')
wizcard_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
wizcard_app.autodiscover_tasks(settings.INSTALLED_APPS + ("lib.emailInvite", "lib.ocr"))

CELERY_IMPORTS=("periodic.tasks",)

@wizcard_app.task(bind=True)
def debug_task(self):
        print('Request: {0!r}'.format(self.request))
