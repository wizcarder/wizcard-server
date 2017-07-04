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

# Create your models here.

class EmailEvent(models.Model):
    NEWUSER = 1
    INVITED = 2
    SCANNED = 3
    NEWRECOMMENDATION = 4
    MISSINGU = 5
    JOINUS = 6
    DIGEST = 7
    INVITE_EXHIBITOR = 8
    EVENTS = (
        (NEWUSER, 'NEWUSER'),
        (INVITED, 'INVITED'),
        (SCANNED, 'SCANNED'),
        (NEWRECOMMENDATION, 'RECOMMENDATION'),
        (MISSINGU, 'MISSINGU'),
        (JOINUS, 'JOINUS'),
        (DIGEST, 'DIGEST'),
        (INVITE_EXHIBITOR, 'INVITE_EXHIBITOR')
    )
    BUFFERED = 1
    INSTANT = 2
    EVENT_TYPE = (
        (BUFFERED, 'BUFFERED'),
        (INSTANT, 'INSTANT')
    )
    event = models.PositiveSmallIntegerField(choices=EVENTS)
    event_type = models.PositiveSmallIntegerField(choices=EVENT_TYPE, default=INSTANT)

    @property
    def get_event_type(self):
        return self.event_type


class EmailAndPushManager(models.Manager):

    def pushEvent(self, sender, event, to, target=None):
        event = EmailEvent.objects.get(event=event)
        sender_content_type = ContentType.objects.get_for_model(sender)

        if target:
            target_content_type = ContentType.objects.get_for_model(target)
            target_object_id = target.id
            to = target.email
            eap, created = EmailAndPush.objects.get_or_create(sender_content_type=sender_content_type, sender_object_id=sender.id, event=event, to=to, target_content_type=target_content_type,
                                                              target_object_id = target_object_id)
        else:
            eap, created = EmailAndPush.objects.get_or_create(sender_content_type=sender_content_type, sender_object_id = sender.id, event=event, to=to)

        return eap


class EmailAndPush(models.Model):
    sender_content_type = models.ForeignKey(ContentType, related_name='email_and_push', default=15)
    sender_object_id = models.PositiveIntegerField()
    sender = generic.GenericForeignKey('sender_content_type', 'sender_object_id')
    event = models.ForeignKey(EmailEvent, related_name='email_event')
    to = EmailField(blank=True)
    target_content_type = models.ForeignKey(ContentType, related_name="email_target", blank=True, null=True)
    target_object_id = models.PositiveIntegerField(null=True, blank=True)
    target = generic.GenericForeignKey('target_content_type', 'target_object_id')
    last_sent = models.DateTimeField(blank=True, null=True)

    objects = EmailAndPushManager()

    @property
    def get_to(self):
        return self.to

    def updateEmailTime(self, sent_time=timezone.now):
        self.last_sent = sent_time

