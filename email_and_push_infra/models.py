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
import pdb
from datetime import timedelta

# Create your models here.


class EmailAndPushManager(models.Manager):

    def candidates(self, reminder_intervals=[1, 3, 5]):

        inst_email_candidates = EmailAndPush.objects.filter(
            event_type=EmailAndPush.INSTANT,
            status=EmailAndPush.NEW,
        )
        inst_notif_candidates = EmailAndPush.objects.filter(
            event_type=EmailAndPush.INSTANT,
            status=EmailAndPush.NEW,
        )

        # Buffered events requires some timestamp calculations using extra deferring it
        # for now but is pretty easy to do.
        return inst_email_candidates, inst_notif_candidates


class EmailAndPush(models.Model):
    NEWUSER = 1
    INVITED = 2
    SCANNED = 3
    NEWRECOMMENDATION = 4
    MISSINGU = 5
    JOINUS = 6
    DIGEST = 7
    INVITE_EXHIBITOR = 8
    INVITE_ATTENDEE = 9

    EVENTS = (
        (NEWUSER, 'NEWUSER'),
        (INVITED, 'INVITED'),
        (SCANNED, 'SCANNED'),
        (NEWRECOMMENDATION, 'RECOMMENDATION'),
        (MISSINGU, 'MISSINGU'),
        (JOINUS, 'JOINUS'),
        (DIGEST, 'DIGEST'),
        (INVITE_EXHIBITOR, 'INVITE_EXHIBITOR'),
        (INVITE_ATTENDEE, 'INVITE_ATTENDEE')
    )

    RECUR = 1
    INSTANT = 2
    SCHEDULED = 3

    EVENT_TYPE = (
        (RECUR, 'RECUR'),
        (INSTANT, 'INSTANT'),
        (SCHEDULED, 'SCHEDULED')
    )

    SUCCESS = 0
    FAILURE = -1
    NEW = 1

    STATUS = (
        (SUCCESS, 'success'),
        (FAILURE, 'failed'),
        (NEW, 'new')
    )

    event_type = models.PositiveSmallIntegerField(choices=EVENT_TYPE, default=INSTANT)
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

