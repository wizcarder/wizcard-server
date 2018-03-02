from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.conf import settings
from .utils import id2slug
from django.utils import timezone
from datetime import timedelta
from notifications.signals import notify
from notifications.push_tasks import push_notification_to_app
from wizserver import verbs
from base_entity.models import BaseEntityComponent


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


class BaseNotificationManager(models.Manager):
    def mark_as_read(self, notifications):
        ids = notifications.values_list('id', flat=True)
        self.filter(pk__in=list(ids)).update(readed=True)


class BaseNotification(models.Model):

    # async goes in EmailPush, sync goes in SyncNotification
    DELIVERY_TYPE_ASYNC = 1
    DELIVERY_TYPE_SYNC = 2

    recipient = models.ForeignKey(User, blank=False, related_name='notifications')
    actor_content_type = models.ForeignKey(ContentType, related_name='notify_actor')
    actor_object_id = models.CharField(max_length=255)
    actor = GenericForeignKey('actor_content_type', 'actor_object_id')

    verb = models.CharField(max_length=255)

    target_content_type = models.ForeignKey(ContentType, related_name='notify_target', blank=True, null=True)
    target_object_id = models.CharField(max_length=255, blank=True, null=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    action_object_content_type = models.ForeignKey(
        ContentType,
        related_name='notify_action_object',
        blank=True,
        null=True
    )
    action_object_object_id = models.CharField(max_length=255, blank=True, null=True)
    action_object = GenericForeignKey('action_object_content_type', 'action_object_object_id')

    timestamp = models.DateTimeField(default=timezone.now)

    public = models.BooleanField(default=True)
    notif_type = models.PositiveIntegerField(default=0)
    readed = models.BooleanField(default=False)

    do_push = models.BooleanField(default=False)
    notification_text = models.CharField(max_length=254, default="")
    notif_operation = models.CharField(max_length=1, default="")

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

    def build_response_dict(self):
        sub_entity_data = ""
        operation=self.notif_operation

        if operation == verbs.NOTIF_OPERATION_CREATE:
            cls, ser = BaseEntityComponent.entity_cls_ser_from_type(self.sub_entity_type, detail=True)
            sub_entity_data = ser(self.action_object, context={'user': self.recipient}).data

        return dict(
            entity_id=self.target.id,
            entity_type=self.target.entity_type,
            sub_entity_id=self.action_object_object_id if self.action_object_object_id else "",
            sub_entity_type=self.action_object.entity_type if self.action_object else "",
            operation=operation,
            sub_entity_data=sub_entity_data,
            message=self.notification_text
        )


class AsyncNotificationManager(BaseNotificationManager):
    def unread(self, **kwargs):
        count = kwargs.pop('count', settings.ASYNC_NOTIF_BATCH_SIZE)
        kwargs.update(readed=False)

        return self.filter(**kwargs)[:count]

    def event_notifications(self, event):
        # this should filter for notifications event.
        # Important: Several notifications may be queued for an Event, this one is specifically
        # those created explicitly by Organizer.
        pass


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

    # Ideally should add interval fields also (periodicity) hardcoding to 1, 3, 5  from the end_date
    objects = AsyncNotificationManager()

    def update_last_tried(self, sent_time=timezone.now):
        self.last_tried = sent_time
        self.save()


class SyncNotificationManager(BaseNotificationManager):
    def unread(self, **kwargs):
        count = kwargs.pop('count', settings.SYNC_NOTIF_BATCH_SIZE)
        kwargs.update(readed=False)

        return self.filter(**kwargs)[:count]

    def unacted(self, user):
        return self.filter(recipient=user, acted_upon=False)

    def unread_count(self, user):
        return self.filter(recipient=user, readed=False).count()

    def migrate_future_user(self, future, current):
        return self.filter(recipient=future.pk).update(recipient=current.pk)


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
    target = kwargs.pop('target', None)
    action_object = kwargs.pop('action_object', None)
    action_object_content_type = ContentType.objects.get_for_model(action_object) if action_object else None
    action_object_object_id = action_object.pk if action_object else None
    start = kwargs.pop('start_date', timezone.now()+timedelta(minutes=1))
    end = kwargs.pop('end_date', start)
    # hidden side-effects of changing do_push to false. Check with me before changing
    do_push = kwargs.pop('do_push', True)
    notif_operation = kwargs.pop('notif_operation', "")

    """
    ASYNC goes in AsyncNotification. SYNC goes in SyncNotification
    """

    if kwargs.pop('force_sync', False):
        is_async = False
    else:
        is_async = verbs.get_notif_is_async(notif_tuple)

    # also check if there is someone to flood to. No point creating notif if no one
    if is_async and target.flood_set(ntuple=notif_tuple, sender=actor):
        newnotify = AsyncNotification.objects.create(
            actor_content_type=ContentType.objects.get_for_model(actor),
            actor_object_id=actor.pk,
            recipient=recipient,
            target_content_type=ContentType.objects.get_for_model(target),
            target_object_id=target.pk,
            action_object_content_type=action_object_content_type,
            action_object_object_id=action_object_object_id,
            readed=False,
            notif_type=verbs.get_notif_type(notif_tuple),
            verb=verbs.get_notif_verb(notif_tuple),
            timestamp=kwargs.pop('timestamp', timezone.now()),
            notif_operation=notif_operation,
            # AA: Comments: EmailPush cannot decide whether this is INSTANT or not.
            delivery_period=AsyncNotification.INSTANT,
            start_date=start,
            end_date=end,
            do_push=do_push,
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
            notif_operation=notif_operation,
            defaults={
                'public': bool(kwargs.pop('public', True)),
                'timestamp': kwargs.pop('timestamp', timezone.now()),
            }
        )

        # push a notification to app from here for sync. Fire and forget
        if created and verbs.get_notif_apns_required(notif_tuple) and do_push:
            push_notification_to_app.delay(newnotify, notif_tuple)

    return newnotify


notify.connect(notify_handler, dispatch_uid='notifications.models.SyncNotification')
