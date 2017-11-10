from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.conf import settings
from .utils import id2slug
from notifications.signals import notify
from email_and_push_infra.models import EmailAndPush
from wizserver import verbs
import logging
import pdb
from datetime import timedelta
from django.utils import timezone

now = timezone.now()



class NotificationManager(models.Manager):
    def unread(self, user, count=settings.NOTIF_BATCH_SIZE):
        return list(self.filter(recipient=user, is_async=False, readed=False)[:count])

    def unacted(self, user):
        return self.filter(recipient=user, is_async=False, acted_upon=False)

    def unread_count(self, user):
        return self.unread(user).count()

    def mark_specific_as_read(self, notifications):
        count = 0
        for n in notifications:
            count += 1
            n.readed = True
            n.save()
        return count

    def mark_all_as_read(self, recipient, count):
        return self.filter(recipient=recipient, is_async=False, readed=False).update(readed=True)

    def migrate_future_user(self, future, current):
        return self.filter(recipient=future.pk).update(recipient=current.pk)

    # AR: TODO this query seems convoluted. It should simply be: verb, target, unreaded
    def get_unread_users(self, verb, filter_users=None):

        qs = self.filter(verb=verb, is_async=False, readed=False)
        if filter_users:
            qs = qs.filter(recipient__in=filter_users)
        exclude_users = map(lambda x: x.recipient, qs)

        return exclude_users

    def async(self):
        return self.filter(is_async=True, readed=False)


class Notification(models.Model):
    """
    unified notification model.
    is_async=True/False is picked up by celery/get_cards respectively

    """

    # used by Portal. ALERT is also used by app for legacy path
    EMAIL = 1
    ALERT = 2

    # used internally as consequence of 2
    PUSHNOTIF = 3

    DELIVERY_TYPE = (
        (EMAIL, 'email'),
        (ALERT, 'alert'),
        (PUSHNOTIF, 'pushnotif'),
    )

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
    delivery_type = models.PositiveSmallIntegerField(choices=DELIVERY_TYPE, default=ALERT)
    is_async = models.BooleanField(default=False)

    recipient = models.ForeignKey(User, blank=False, related_name='notifications')
    readed = models.BooleanField(default=False, blank=False)

    # new one to support resync of "un-acted-upon" notifs. We will set this
    # flag to False for user exposed notifs (type 2 currently) when we create
    # those specific notifs. App implicitly lets us know that it has acted on it
    # by passing notif_id in the associated message that caused the action
    # (accept_connection_request, decline_connection_request) at which point we set
    # the flag back to True
    acted_upon = models.BooleanField(default=True, blank=False)

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

    email_push = models.ForeignKey(EmailAndPush, related_name='email_push_notif', blank=True, null=True)

    timestamp = models.DateTimeField(default=timezone.now)

    public = models.BooleanField(default=True)
    notif_type = models.PositiveIntegerField()

    objects = NotificationManager()

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
    is_async = kwargs.pop('is_async', False)
    delivery_type = kwargs.pop('delivery_type', Notification.ALERT)
    verb = kwargs.pop('verb', "")
    target = kwargs.pop('target', None)
    action_object = kwargs.pop('action_object', None)
    action_object_content_type = ContentType.objects.get_for_model(action_object) if action_object else None
    action_object_object_id = action_object.pk if action_object else None
    push_obj = None

    if is_async:
        start = kwargs.pop('start_date', timezone.now() + timedelta(minutes=1))
        end = kwargs.pop('end_date', start)

        # AA: Comments: EmailPush cannot decide whether this is INSTANT or not. It has to come from top
        # It might need additional fields in the REST API. Think about usecases. For example, if the portal
        # user ties a push to a speaker session in the agenda. Portal will digest this, create some information
        # to figure out when start-stop should be. Alternatively, it could be something that allows REST api to indicate
        # that this is tied to this entity.
        # net-net, pls think top-down, of all potential use-cases of what/why it's being implemented and construct
        # the code architecture to span all those cases. We may not implement all those at once, but the arch
        # should be extensible

        # action obj for async is always EmailAndPush
        push_obj = EmailAndPush.objects.create(event_type=EmailAndPush.INSTANT, start_date=start, end_date=end)

        # if push_notif needs to be sent
        do_push = bool(kwargs.pop('do_push', False))

    else:
        # AA: TODO : The get_cards push determination can be done in a better way by combining
        # apns_notification_dictionary & (Verb, APNS_REQUIRED, APNS_TEXT) tuple list

        do_push = notif_type in verbs.apns_notification_dictionary
        start = end = timezone.now()

    if do_push:
        # create EmailPush and Notif
        push_obj = EmailAndPush.objects.create(
            event_type=EmailAndPush.INSTANT,
            start_date=start,
            end_date=end
        )

        Notification.objects.create(
            actor_content_type=ContentType.objects.get_for_model(actor),
            actor_object_id=actor.pk,
            recipient=recipient,
            readed=False,
            is_async=True,
            delivery_type=Notification.PUSHNOTIF,
            notif_type=notif_type,
            verb=verb,
            target_content_type=ContentType.objects.get_for_model(target),
            target_object_id=target.pk,
            email_push=push_obj,
            action_object_content_type=action_object_content_type,
            action_object_object_id=action_object_object_id,
            public=bool(kwargs.pop('public', True)),
            timestamp=kwargs.pop('timestamp', now())
        )

    is_async = False if delivery_type == Notification.ALERT else True

    newnotify, created = Notification.objects.get_or_create(
        actor_content_type=ContentType.objects.get_for_model(actor),
        actor_object_id=actor.pk,
        recipient=recipient,
        readed=False,
        delivery_type=delivery_type,
        notif_type=notif_type,
        verb=verb,
        target_content_type=ContentType.objects.get_for_model(target),
        target_object_id=target.pk,
        email_push=push_obj,
        defaults={
            'is_async': is_async,
            'action_object_content_type': action_object_content_type,
            'action_object_object_id': action_object_object_id,
            'public': bool(kwargs.pop('public', True)),
            'timestamp': kwargs.pop('timestamp', now())
        }
    )

    return newnotify


# connect the signal
notify.connect(notify_handler, dispatch_uid='notifications.models.notification')
