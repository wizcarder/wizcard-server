"""
.. autoclass:: EmailAndPush
    :members:

.. autoclass:: EmailAndPushManager
    :members:

.. autoclass:: EmailEvent
    :members:
"""

from django.db import models
from wizcardship.models import Wizcard
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from base.emailField import EmailField
from entity.models import Event
import datetime
from django.utils import timezone
import pdb
from datetime import datetime, timedelta

# Create your models here.


class EmailAndPushManager(models.Manager):

    def pushEvent(self, sender, event, event_type=INSTANT, delivery, target=None):
        sender_content_type = ContentType.objects.get_for_model(sender)


        target_content_type = ContentType.objects.get_for_model(target)
        target_object_id = target.id

        eap, created = EmailAndPush.objects.get_or_create(sender_content_type=sender_content_type,
                                                          sender_object_id=sender.id,
                                                          event=event,
                                                          event_type=event_type,
                                                          delivery=delivery,
                                                          target_content_type=target_content_type,
                                                          target_object_id = target_object_id)

        return eap

    def candidates(self, reminder_intervals=[1, 3, 5]):

        inst_email_candidates = EmailAndPush.objects.filter(event_type=EmailAndPush.INSTANT, status=EmailAndPush.NEW, delivery=EmailAndPush.EMAIL)
        inst_notif_candidates = EmailAndPush.objects.filter(event_type=EmailAndPush.INSTANT, status=EmailAndPush.NEW, delivery=EmailAndPush.PUSHNOTIF)

        ## Buffered events requires some timestamp calculations using extra deferring it for now but is pretty easy to do.

        return (inst_email_candidates, inst_notif_candidates)



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
    BUFFERED = 1
    INSTANT = 2
    EVENT_TYPE = (
        (BUFFERED, 'BUFFERED'),
        (INSTANT, 'INSTANT')
    )


    EMAIL = 1
    PUSHNOTIF = 2
    SMS = 3

    DELIVERY = (
        (EMAIL, 'email'),
        (PUSHNOTIF, 'pushnotif'),
        (SMS, 'sms')
    )
    SUCCESS = 0
    FAILURE = -1
    NEW = 1
    STATUS = (
        (SUCCESS, 'success'),
        (FAILURE, 'failed'),
        (NEW, 'new')
    )
    sender_content_type = models.ForeignKey(ContentType, related_name='email_and_push', default=15)
    sender_object_id = models.PositiveIntegerField()
    sender = generic.GenericForeignKey('sender_content_type', 'sender_object_id')
    event = models.PositiveSmallIntegerField(choices=EVENTS)
    event_type = models.PositiveSmallIntegerField(choices=EVENT_TYPE, default=INSTANT)
    target_content_type = models.ForeignKey(ContentType, related_name="email_target", blank=True, null=True)
    target_object_id = models.PositiveIntegerField(null=True, blank=True)
    target = generic.GenericForeignKey('target_content_type', 'target_object_id')
    last_tried = models.DateTimeField(blank=True, null=True)
    delivery = models.PositiveSmallIntegerField(choices=DELIVERY)
    created = models.DateTimeField(auto_now=True)
    status = models.PostiveSmallIntegerField(choices=STATUS, default=NEW)
    start_date = models.DateTimeField(default=timezone.now())
    end_date = models.DateTimeField(default=timezone.now() + timedelta(days=5))

    #Ideally should add interval fields also (periodicity) hardcoding to 1, 3, 5  from the end_date


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

    def instant_candidates(self):
        self.

