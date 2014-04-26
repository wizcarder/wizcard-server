from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.utils import timezone
from django.conf import settings
from .utils import id2slug
from notifications.signals import notify
from pyapns import notify as apns_notify
from pyapns import configure, provision
import pdb


try:
    from django.utils import timezone
    now = timezone.now
except ImportError:
    now = datetime.datetime.now()

class NotificationManager(models.Manager):
    def unread(self, user):
        return self.filter(recipient=user, readed=False)

    def unread_count(self, user):
        return self.unread.count()

    def mark_all_as_read(self, recipient):
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
    WIZREQ_U = 'wizconnection request untrusted'
    WIZREQ_T = 'wizconnection request trusted'
    WIZ_ACCEPT = 'accepted wizcard'
    WIZ_REVOKE = 'revoked wizcard'
    WIZ_DELETE = 'deleted wizcard'
    WIZ_TABLE_TIMEOUT = 'table timeout'
    WIZ_TABLE_DESTROY = 'table destroy'
    WIZ_CARD_UPDATE = 'wizcard update'
    WIZ_CARD_FLICK_TIMEOUT = 'flick timeout'



    apns_notification_dictionary = {
        WIZREQ_U	: {
		'sound': 'flynn.caf',
		'badge': 0,
		'message': WIZREQ_U,
		},
	WIZREQ_T	: {
		'sound': 'flynn.caf',
		'badge': 0,
		'message': WIZREQ_U,
		},
	WIZ_ACCEPT: {
		'sound': 'flynn.caf',
		'badge': 0,
		'message': WIZREQ_U,
		},
	WIZ_REVOKE: {
		'sound': 'flynn.caf',
		'badge': 0,
		'message': WIZREQ_U,
		},
	WIZ_DELETE: {
		'sound': 'flynn.caf',
		'badge': 0,
		'message': WIZREQ_U,
		},
	WIZ_TABLE_TIMEOUT: {
		'sound': 'flynn.caf',
		'badge': 0,
		'message': WIZREQ_U,
		},
	WIZ_TABLE_TIMEOUT: {
		'sound': 'flynn.caf',
		'badge': 0,
		'message': WIZREQ_U,
		},
	WIZ_CARD_UPDATE: {
		'sound': 'flynn.caf',
		'badge': 0,
		'message': WIZREQ_U,
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
        ordering = ('-timestamp', )

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
        push_to_app_handler = {
            UserProfile.IOS	: self.pushIOS,
            UserProfile.ANDROID	: self.pushAndroid
        }
        #push_to_app_handler[receiver.device_type](receiver, sender, verb)

    def pushIOS(self, receiver, sender, verb):
	apns_notify('wizcard-ios', 
		    receiver.reg_token, 
		    self.apns_notification_dictionary[verb])

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
    if not profile.online():
        newnotify.pushNotificationToApp(
			profile,
			actor,
			verb)

# connect the signal
notify.connect(notify_handler, dispatch_uid='notifications.models.notification')
