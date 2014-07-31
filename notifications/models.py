from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.utils import timezone
from django.conf import settings
from .utils import id2slug
from notifications.signals import notify
from pyapns import notify as apns_notify
from pyapns import configure, provision, feedback
import logging
import pdb


try:
    from django.utils import timezone
    now = timezone.now
except ImportError:
    now = datetime.datetime.now()

class NotificationManager(models.Manager):
    def unread(self, user, count=settings.NOTIF_BATCH_SIZE):
        return list(self.filter(recipient=user, readed=False)[:count])

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
    DEFAULT_MSG = 'wizcard message'
    WIZREQ_U = 'wizconnection request untrusted'
    WIZREQ_T = 'wizconnection request trusted'
    WIZCARD_ACCEPT = 'accepted wizcard'
    WIZCARD_REVOKE = 'revoked wizcard'
    WIZCARD_WITHDRAW_REQUEST = 'withdraw request'
    WIZCARD_DELETE = 'deleted wizcard'
    WIZCARD_TABLE_TIMEOUT = 'table timeout'
    WIZCARD_TABLE_DESTROY = 'table destroy'
    WIZCARD_UPDATE = 'wizcard update'
    WIZCARD_FLICK_TIMEOUT = 'flick timeout'
    WIZCARD_FLICK_PICK = 'flick pick'



    apns_notification_dictionary = {
        DEFAULT_MSG     : {
		'sound': 'flynn.caf',
		'badge': 0,
                #AA:TODO: separate verb from push message
		'alert': DEFAULT_MSG,
		},
        WIZREQ_U	: {
		'sound': 'flynn.caf',
		'badge': 0,
                #AA:TODO: separate verb from push message
		'alert': WIZREQ_U,
		},
        WIZREQ_U	: {
		'sound': 'flynn.caf',
		'badge': 0,
		'alert': WIZREQ_U,
		},
	WIZREQ_T	: {
		'sound': 'flynn.caf',
		'badge': 0,
		'alert': WIZREQ_T,
		},
	WIZCARD_ACCEPT: {
		'sound': 'flynn.caf',
		'badge': 0,
		'alert': WIZCARD_ACCEPT,
		},
	WIZCARD_REVOKE: {
		'sound': 'flynn.caf',
		'badge': 0,
		'alert': WIZCARD_REVOKE,
		},
	WIZCARD_WITHDRAW_REQUEST: {
		'sound': 'flynn.caf',
		'badge': 0,
		'alert': WIZCARD_WITHDRAW_REQUEST,
		},
	WIZCARD_DELETE: {
		'sound': 'flynn.caf',
		'badge': 0,
		'alert': WIZCARD_DELETE,
		},
	WIZCARD_TABLE_TIMEOUT: {
		'sound': 'flynn.caf',
		'badge': 0,
		'alert': WIZCARD_TABLE_TIMEOUT,
		},
	WIZCARD_TABLE_DESTROY: {
		'sound': 'flynn.caf',
		'badge': 0,
		'alert': WIZCARD_TABLE_DESTROY,
		},
	WIZCARD_UPDATE: {
		'sound': 'flynn.caf',
		'badge': 0,
		'alert': WIZCARD_UPDATE,
		},
	WIZCARD_FLICK_TIMEOUT: {
		'sound': 'flynn.caf',
		'badge': 0,
		'alert': WIZCARD_FLICK_TIMEOUT,
		},
	WIZCARD_FLICK_PICK: {
		'sound': 'flynn.caf',
		'badge': 0,
		'alert': WIZCARD_FLICK_PICK,
		},
    }

    recipient = models.ForeignKey(User, blank=False, related_name='notifications')
    readed = models.BooleanField(default=False, blank=False)

    actor_content_type = models.ForeignKey(ContentType, related_name='notify_actor')
    actor_object_id = models.CharField(max_length=255)
    actor = generic.GenericForeignKey('actor_content_type', 'actor_object_id')

    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    target_content_type = models.ForeignKey(ContentType, related_name='notify_target',
        blank=True, null=True)
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

    def pushNotificationToApp(self, receiver, sender, verb):
        from userprofile.models import UserProfile
        if not self.apns_notification_dictionary.has_key(verb):
            apns_message = dict(aps=self.apns_notification_dictionary[self.DEFAULT_MSG])
        else:
            apns_message = dict(aps=self.apns_notification_dictionary[verb])

        push_to_app_handler = {
            UserProfile.IOS	: self.pushIOS,
            UserProfile.ANDROID	: self.pushAndroid
        }
        push_to_app_handler[receiver.device_type](receiver, sender, apns_message)

    def pushIOS(self, receiver, sender, apns_message):
	apns_notify(settings.APP_ID,
		    receiver.reg_token, 
		    apns_message)

        return

    def pushAndroid(self, receiver, sender, verb):
	send_gcm_message(settings.GCM_API_KEY, 
			receiver.reg_token,
			self.apns_notification_dictionary[verb])
        return

def notify_handler(verb, **kwargs):
    """
    Handler function to create Notification instance upon action signal call.
    """
    kwargs.pop('signal', None)
    recipient = kwargs.pop('recipient')
    actor = kwargs.pop('sender')
    newnotify = Notification(
        recipient = recipient,
        actor_content_type=ContentType.objects.get_for_model(actor),
        actor_object_id=actor.pk,
        verb=unicode(verb),
        public=bool(kwargs.pop('public', True)),
        description=kwargs.pop('description', None),
        timestamp=kwargs.pop('timestamp', now())
    )

    for opt in ('target', 'action_object'):
        obj = kwargs.pop(opt, None)
        if not obj is None:
            setattr(newnotify, '%s_object_id' % opt, obj.pk)
            setattr(newnotify, '%s_content_type' % opt,
                    ContentType.objects.get_for_model(obj))

    newnotify.save()

    #check if the target user is online and do APNS if not
    profile = recipient.profile
    if not profile.is_online():
        logging.info("User %(e1) is OFFLINE", extra={'e1':profile.userid})
        newnotify.pushNotificationToApp(
			profile,
			actor,
			verb)

# connect the signal
notify.connect(notify_handler, dispatch_uid='notifications.models.notification')
