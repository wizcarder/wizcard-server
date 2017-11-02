from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.utils import timezone
from django.conf import settings
from .utils import id2slug
from notifications.signals import notify
from notifications.tasks import pushNotificationToApp
from wizserver import  verbs
import logging
import pdb


try:
    from django.utils import timezone
    now = timezone.now
except ImportError:
    from datetime import datetime
    now = datetime.datetime.now()

class NotificationManager(models.Manager):
    def unread(self, user, count=settings.NOTIF_BATCH_SIZE):
        return list(self.filter(recipient=user, readed=False)[:count])

    def unacted(self, user):
        return self.filter(recipient=user, acted_upon=False)

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
        return self.filter(recipient=recipient, readed=False).update(readed=True)

    def migrate_future_user(self, future, current):
        return self.filter(recipient=future.pk).update(recipient=current.pk)

    # AR: TODO this query seems convoluted. It should simply be: verb, target, unreaded
    def get_unread_users(self, verb, filter_users=None):

        qs = self.filter(verb=verb, readed=False)
        if filter_users:
            qs = qs.filter(recipient__in=filter_users)
        exclude_users = map(lambda x: x.recipient, qs)

        return exclude_users


class Notification(models.Model):
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
    target = generic.GenericForeignKey('target_content_type',
        'target_object_id')

    action_object_content_type = models.ForeignKey(ContentType,
        related_name='notify_action_object', blank=True, null=True)
    action_object_object_id = models.CharField(max_length=255, blank=True,
        null=True)
    action_object = generic.GenericForeignKey('action_object_content_type',
        'action_object_object_id')

    timestamp = models.DateTimeField(default=now)

    public = models.BooleanField(default=True)

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

def notify_handler(verb, **kwargs):
    """
    Handler function to create Notification instance upon action signal call.
    """

    kwargs.pop('signal', None)
    recipient = kwargs.pop('recipient')
    actor = kwargs.pop('sender')
    onlypush = kwargs.pop('onlypush', False)

    if not onlypush:
        newnotify, created = Notification.objects.get_or_create(
            recipient=recipient,
            verb=unicode(verb),
            readed=False,
            defaults={
                'actor_content_type': ContentType.objects.get_for_model(actor),
                'actor_object_id': actor.pk,
                'public': bool(kwargs.pop('public', True)),
                'timestamp': kwargs.pop('timestamp', now())
            }
        )

        if not created:
            return

        for opt in ('target', 'action_object'):
            obj = kwargs.pop(opt, None)
            if not obj is None:
                setattr(newnotify, '%s_object_id' % opt, obj.pk)
                setattr(newnotify, '%s_content_type' % opt,
                    ContentType.objects.get_for_model(obj))
                setattr(newnotify, '%s' % opt, obj)

        newnotify.save()

        pushNotificationToApp.delay(
            newnotify.actor_object_id,
            newnotify.recipient_id,
            newnotify.action_object_object_id,
            newnotify.action_object_content_type,
            newnotify.target_object_id,
            newnotify.target_content_type,
            newnotify.verb
            )
    else:
        pushparam = dict()
        verb = unicode(verb)
        for opt in ('target','action_object'):
            obj = kwargs.pop(opt, None)
            if not obj is None:
                tkey = '%s_object_id' % opt
                pushparam[tkey] = obj.pk
                tkey = '%s_content_type' % opt
                pushparam[tkey] = ContentType.objects.get_for_model(obj)
            else:
                tkey = '%s_object_id' % opt
                pushparam[tkey] = None
                tkey = '%s_content_type' % opt
                pushparam[tkey] = None

        pushNotificationToApp.delay(
            actor.pk,
            recipient.pk,
            pushparam['action_object_object_id'],
            pushparam['action_object_content_type'],
            pushparam['target_object_id'],
            pushparam['target_content_type'],
            verb
            )

    #    except:
    #        logging.error("Failed to send APNS to User %s",
    #                recipient.profile.userid)

# connect the signal
notify.connect(notify_handler, dispatch_uid='notifications.models.notification')
