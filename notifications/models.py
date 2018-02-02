from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.conf import settings
from .utils import id2slug
from django.utils import timezone
from datetime import timedelta
from notifications.signals import notify
from notifications.push_tasks import push_notification_to_app
from wizserver import verbs


import pdb


now = timezone.now()

"""
   Action model describing the actor acting out a verb (on an optional
   target).
   Nomenclature based on http://activitystrea.ms/specs/atom/1.0/

   Generalized Format::

       <actor> <verb> <time>
       <actor> <verb> <target> <time>
       <actor> <verb> <action_object> <target> <time>

   Examples::

       <justquick> <reached level 60> <1 minute ago>
       <brosner> <commented on> <pinax/pinax> <2 hours ago>
       <washingtontimes> <started follow> <justquick> <8 minutes ago>
       <mitsuhiko> <closed> <issue 70> on <mitsuhiko/flask> <about 2 hours ago>

   Unicode Representation::

       justquick reached level 60 1 minute ago
       mitsuhiko closed issue 70 on mitsuhiko/flask 3 hours ago

   HTML Representation::

       <a href="http://oebfare.com/">brosner</a> commented on <a href="http://github.com/pinax/pinax">pinax/pinax</a> 2 hours ago

   """

class BaseNotification(models.Model):
    DELIVERY_MODE_EMAIL = 1
    DELIVERY_MODE_ALERT = 2

    DELIVERY_MODE = (
        (DELIVERY_MODE_EMAIL, 'email'),
        (DELIVERY_MODE_ALERT, 'alert')
    )

    # async goes in EmailPush, sync goes in SyncNotification
    DELIVERY_TYPE_ASYNC = 1
    DELIVERY_TYPE_SYNC = 2

    delivery_mode = models.PositiveSmallIntegerField(choices=DELIVERY_MODE, default=DELIVERY_MODE_ALERT)

    recipient = models.ForeignKey(User, blank=False, related_name='notifications')
    actor_content_type = models.ForeignKey(ContentType, related_name='notify_actor')
    actor_object_id = models.CharField(max_length=255)
    actor = generic.GenericForeignKey('actor_content_type', 'actor_object_id')

    verb = models.CharField(max_length=255)

    target_content_type = models.ForeignKey(ContentType, related_name='notify_target', blank=True, null=True)
    target_object_id = models.CharField(max_length=255, blank=True, null=True)
    target = generic.GenericForeignKey('target_content_type', 'target_object_id')

    action_object_content_type = models.ForeignKey(
        ContentType,
        related_name='notify_action_object',
        blank=True,
        null=True
    )
    action_object_object_id = models.CharField(max_length=255, blank=True, null=True)
    action_object = generic.GenericForeignKey('action_object_content_type', 'action_object_object_id')

    timestamp = models.DateTimeField(default=timezone.now)

    public = models.BooleanField(default=True)
    notif_type = models.PositiveIntegerField(default=0)
    readed = models.BooleanField(default=False)

    class Meta:
        ordering = ('timestamp', )

    def __unicode__(self):
        ctx = {
            'actor': self.actor,
            'verb': self.verb,
            'action_object': self.action_object,
            'target': self.target,
            'timesince': self.timesince()
        }
        if self.target:
            if self.action_object:
                return '%(actor)s %(verb)s %(action_object)s on %(target)s %(timesince)s ago' % ctx
            return '%(actor)s %(verb)s %(target)s %(timesince)s ago' % ctx
        if self.action_object:
            return '%(actor)s %(verb)s %(action_object)s %(timesince)s ago' % ctx
        return '%(actor)s %(verb)s %(timesince)s ago' % ctx

    def timesince(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the
        current timestamp.
        """
        from django.utils.timesince import timesince as timesince_
        return timesince_(self.timestamp, now)

    @property
    def slug(self):
        return id2slug(self.id)

    def update_status(self, status):
        self.status = status
        self.save()

    def mark_as_read(self):
        if not self.readed:
            self.readed = True
            self.save()


class AsyncNotificationManager(models.Manager):
    def unread(self, **kwargs):
        count = kwargs.pop('count', settings.ASYNC_NOTIF_BATCH_SIZE)
        kwargs.update(readed=False)

        return self.filter(**kwargs)[:count]


# AA: Comment: This should probably be renamed to AsyncNotif
class AsyncNotification(BaseNotification):

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
    last_tried = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now=True)
    status = models.PositiveSmallIntegerField(choices=STATUS, default=NEW)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    notifcation_text = models.CharField(max_length=100, default="")

    # Ideally should add interval fields also (periodicity) hardcoding to 1, 3, 5  from the end_date
    objects = AsyncNotificationManager()

    def update_last_tried(self, sent_time=timezone.now):
        self.last_tried = sent_time
        self.save()


class SyncNotificationManager(models.Manager):
    def unread(self, **kwargs):
        count = kwargs.pop('count', settings.SYNC_NOTIF_BATCH_SIZE)
        kwargs.update(readed=False)

        return self.filter(**kwargs)[:count]

    def unacted(self, user):
        return self.filter(recipient=user, acted_upon=False)

    def unread_count(self, user):
        return self.filter(recipient=user, readed=False).count()

    def mark_specific_as_read(self, notifications):
        count = 0
        for n in notifications:
            count += 1
            n.readed = True
            n.save()
        return count

    def mark_all_as_read(self, recipient):
        return self.filter(recipient=recipient, readed=False).update(readed=True)

    def migrate_future_user(self, future, current):
        return self.filter(recipient=future.pk).update(recipient=current.pk)

    def event_notifications(self, event):
        # this should filter for notifications event.
        # Important: Several notifications may be queued for an Event, this one is specifically
        # those created explicitly by Organizer.
        pass


class SyncNotification(BaseNotification):
    acted_upon = models.BooleanField(default=True, blank=False)

    objects = SyncNotificationManager()

    def set_acted(self, flag):
        self.acted_upon = flag
        self.save()


# Event based Triggers
TRIGGER_NEW_USER = 1
TRIGGER_PENDING_INVITE = 2
TRIGGER_CONNECTION_ACCEPTED = 3
TRIGGER_RECOMMENDATION_AVAILABLE = 4
TRIGGER_SCAN_CARD = 5

# Generic Triggers
TRIGGER_WEEKLY_DIGEST = 11


def notify_handler(sender, **kwargs):
    """
    Handler function to create SyncNotification instance upon action signal call.
    """

    kwargs.pop('signal', None)
    actor = sender
    recipient = kwargs.pop('recipient')
    notif_tuple = kwargs.pop('notif_tuple')
    delivery_mode = kwargs.pop('delivery_mode', BaseNotification.DELIVERY_MODE_ALERT)
    target = kwargs.pop('target', None)
    action_object = kwargs.pop('action_object', None)
    action_object_content_type = ContentType.objects.get_for_model(action_object) if action_object else None
    action_object_object_id = action_object.pk if action_object else None
    do_push = kwargs.pop('do_push', False)
    start = kwargs.pop('start_date', timezone.now()+timedelta(minutes=1))
    end = kwargs.pop('end_date', start)

    """
    ASYNC goes in AsyncNotification. SYNC goes in SyncNotification
    """

    if kwargs.pop('force_sync', False):
        is_async = False
    else:
        is_async = verbs.get_notif_is_async(notif_tuple)

    if is_async:
        newnotify = AsyncNotification.objects.create(
            actor_content_type=ContentType.objects.get_for_model(actor),
            actor_object_id=actor.pk,
            recipient=recipient,
            target_content_type=ContentType.objects.get_for_model(target),
            target_object_id=target.pk,
            action_object_content_type=action_object_content_type,
            action_object_object_id=action_object_object_id,
            readed=False,
            delivery_mode=delivery_mode,
            notif_type=verbs.get_notif_type(notif_tuple),
            verb=verbs.get_notif_verb(notif_tuple),
            timestamp=kwargs.pop('timestamp', timezone.now()),
            # AA: Comments: EmailPush cannot decide whether this is INSTANT or not.
            delivery_period=AsyncNotification.INSTANT,
            start_date=start,
            end_date=end,
            **kwargs
        )
    else:
        newnotify, created = SyncNotification.objects.get_or_create(
            actor_content_type=ContentType.objects.get_for_model(actor),
            actor_object_id=actor.pk,
            recipient=recipient,
            readed=False,
            notif_type=verbs.get_notif_type(notif_tuple),
            verb=verbs.get_notif_verb(notif_tuple),
            target_content_type=ContentType.objects.get_for_model(target),
            target_object_id=target.pk,
            action_object_content_type=action_object_content_type,
            action_object_object_id=action_object_object_id,
            defaults={
                'public': bool(kwargs.pop('public', True)),
                'timestamp': kwargs.pop('timestamp', timezone.now()),
            }
        )

        # push a notification to app from here. Fire and forget
        if created and verbs.get_notif_apns_required(notif_tuple):
            push_notification_to_app.delay(
                newnotify.actor_object_id,
                newnotify.recipient_id,
                newnotify.action_object_object_id,
                newnotify.action_object_content_type,
                newnotify.target_object_id,
                newnotify.target_content_type,
                newnotify.verb
            )

    return newnotify

notify.connect(notify_handler, dispatch_uid='notifications.models.SyncNotification')
