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
from wizserver import verbs
import pdb

# Create your models here.


class EmailAndPushManager(BaseNotificationManager):

    def unread(self):
        return EmailAndPush.objects.filter(readed=False)

    def get_broadcast(self):
        return EmailAndPush.objects.filter(readed=False, notif_type=verbs.WIZCARD_ENTITY_BROADCAST_CREATE[0])



class EmailAndPush(BaseNotification):

    RECUR = 1
    INSTANT = 2
    SCHEDULED = 3

    DELIVERY_PERIOD = (
        (RECUR, 'RECUR'),
        (INSTANT, 'INSTANT'),
        (SCHEDULED, 'SCHEDULED')
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
    delivery_method = models.PositiveSmallIntegerField(choices=BaseNotification.DELIVERY_METHOD, default=BaseNotification.EMAIL)
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

    def mark_as_read(self):
        if not self.readed:
            self.readed = True
            self.save()

