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

    def unread_notifs(self, delivery_method=None):
        return EmailAndPush.objects.filter(readed=False, delivery_method=delivery_method)

    def unread_notifs_by_verb(self, delivery_method=BaseNotification.PUSHNOTIF, verb=verbs.WIZCARD_ENTITY_UPDATE[1]):
        qs = self.unread_notifs(delivery_method)
        qs.filter(verb=verb)
        return qs

    def get_unread_verbs(self, delivery_method=BaseNotification.PUSHNOTIF):
        qs = list(self.unread_notifs(delivery_method).values_list('verb', flat=True).distinct())
        return qs


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

