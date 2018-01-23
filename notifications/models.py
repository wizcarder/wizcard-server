from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.conf import settings
from .utils import id2slug
from notifications.signals import notify
from wizserver import verbs
import logging
import pdb
from datetime import timedelta
from django.utils import timezone
from notifications.tasks import fanout_notifs



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
    pass


class BaseNotification(models.Model):
    EMAIL = 1
    ALERT = 2
    PUSHNOTIF = 3

    DELIVERY_MODE = (
        (EMAIL, 'email'),
        (ALERT, 'alert'),
        (PUSHNOTIF, 'pushnotif'),
    )

    # async goes in EmailPush, sync goes in Notification
    DELIVERY_TYPE_ASYNC = 1
    DELIVERY_TYPE_SYNC = 2

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

    objects = BaseNotificationManager()

    class Meta:
        ordering = ('timestamp', )


class NotificationManager(BaseNotificationManager):
    def unread(self, user, count=settings.NOTIF_BATCH_SIZE):
        return list(self.filter(recipient=user, readed=False)[:count])

    def unacted(self, user):
        return self.filter(recipient=user,  acted_upon=False)

    def unread_count(self, user):
        return self.filter(recipient=user,  readed=False).count()

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


class Notification(BaseNotification):
    acted_upon = models.BooleanField(default=True, blank=False)

    objects = NotificationManager()

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

    def mark_as_read(self):
        if not self.readed:
            self.readed = True
            self.save()

    def set_acted(self, flag):
        self.acted_upon = flag
        self.save()

    def update_status(self, status):
        self.status = status
        self.save()


def notify_handler(notif_type, **kwargs):
    """
    Handler function to create Notification instance upon action signal call.
    """

    kwargs.pop('signal', None)
    recipient = kwargs.pop('recipient')
    actor = kwargs.pop('sender')
    delivery_mode = kwargs.pop('delivery_mode', BaseNotification.ALERT)
    verb = kwargs.pop('verb', "")
    target = kwargs.pop('target', None)
    action_object = kwargs.pop('action_object', None)
    action_object_content_type = ContentType.objects.get_for_model(action_object) if action_object else None
    action_object_object_id = action_object.pk if action_object else None
    do_push = kwargs.pop('do_push', False)
    start = kwargs.pop('start_date', timezone.now() + timedelta(minutes=1))
    end = kwargs.pop('end_date', start)

    from email_and_push_infra.models import EmailAndPush

    if delivery_mode == BaseNotification.EMAIL:
        newnotify = EmailAndPush.objects.create(
            actor_content_type=ContentType.objects.get_for_model(actor),
            actor_object_id=actor.pk,
            recipient=recipient,
            target_content_type=ContentType.objects.get_for_model(target),
            target_object_id=target.pk,
            action_object_content_type=action_object_content_type,
            action_object_object_id=action_object_object_id,
            readed=False,
            delivery_mode=delivery_mode,
            notif_type=notif_type,
            verb=verb,
            timestamp=kwargs.pop('timestamp', timezone.now()),
            # AA: Comments: EmailPush cannot decide whether this is INSTANT or not.
            delivery_period=EmailAndPush.INSTANT,
            start_date=start,
            end_date=end
        )
    else:
        do_push = notif_type in verbs.apns_notification_dictionary or do_push

        if do_push:
            from email_and_push_infra.tasks import pushNotificationToApp
            pushNotificationToApp.delay(
                actor.pk,
                recipient.id,
                action_object_object_id,
                action_object_content_type,
                target.pk,
                ContentType.objects.get_for_model(target),
                notif_type,
                verb,
            )

        newnotify, created = Notification.objects.get_or_create(
            actor_content_type=ContentType.objects.get_for_model(actor),
            actor_object_id=actor.pk,
            recipient=recipient,
            readed=False,
            notif_type=notif_type,
            verb=verb,
            target_content_type=ContentType.objects.get_for_model(target),
            target_object_id=target.pk,
            action_object_content_type=action_object_content_type,
            action_object_object_id=action_object_object_id,
            defaults={
                'public': bool(kwargs.pop('public', True)),
                'timestamp': kwargs.pop('timestamp', timezone.now())
            }
        )

    return newnotify


# connect the signal
notify.connect(notify_handler, dispatch_uid='notifications.models.notification')
