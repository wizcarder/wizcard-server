"""
.. autoclass:: EmailAndPush
    :members:

.. autoclass:: EmailAndPushManager
    :members:

.. autoclass:: EmailEvent
    :members:
"""

from django.db import models
from django.utils import timezone
from notifications.models import BaseNotification, BaseNotificationManager
import pdb

# Create your models here.


class EmailAndPushManager(BaseNotificationManager):

    def candidates(self, reminder_intervals=[1, 3, 5]):

        inst_email_candidates = EmailAndPush.objects.filter(
            delivery_period=EmailAndPush.INSTANT,
            status=EmailAndPush.NEW,
        )
        inst_notif_candidates = EmailAndPush.objects.filter(
            delivery_period=EmailAndPush.INSTANT,
            status=EmailAndPush.NEW,
        )

        # Buffered events requires some timestamp calculations using extra deferring it
        # for now but is pretty easy to do.
        return inst_email_candidates, inst_notif_candidates


class EmailAndPush(BaseNotification):


    RECUR = 1
    INSTANT = 2
    SCHEDULED = 3

    EMAIL = 1
    ALERT = 2
    PUSHNOTIF = 3
    SMS = 4

    DELIVERY_PERIOD = (
        (RECUR, 'RECUR'),
        (INSTANT, 'INSTANT'),
        (SCHEDULED, 'SCHEDULED')
    )

    DELIVERY_METHOD = (
        (EMAIL, 'email'),
        (ALERT, 'alert'),
        (PUSHNOTIF, 'pushnotif'),
        (SMS, 'sms')
    )

    @property
    def get_delivery_period(self):
        return self.delivery_period


    SUCCESS = 0
    FAILURE = -1
    NEW = 1

    STATUS = (
        (SUCCESS, 'success'),
        (FAILURE, 'failed'),
        (NEW, 'new')
    )

    delivery_period = models.PositiveSmallIntegerField(choices=DELIVERY_PERIOD, default=INSTANT)
    delivery_method = models.PositiveSmallIntegerField(choices=DELIVERY_METHOD, default=EMAIL)
    readed = models.BooleanField(default=False)
    last_tried = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now=True)
    status = models.PositiveSmallIntegerField(choices=STATUS, default=NEW)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)

    # Ideally should add interval fields also (periodicity) hardcoding to 1, 3, 5  from the end_date
    objects = EmailAndPushManager()

    @property
    def get_to(self):
        return self.to

    def update_last_tried(self, sent_time=timezone.now):
        self.last_tried = sent_time
        self.save()

    def update_status(self, status):
        self.status = status
        self.save()

