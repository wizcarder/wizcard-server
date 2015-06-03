from celery import shared_task
from celery.contrib import rdb
from wizserver import verbs
from pyapns import notify as apns_notify
from pyapns import configure, provision, feedback
from django.conf import settings
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

@shared_task(ignore_result=True)
def pushNotificationToApp(
        sender_id,
        receiver_id,
        action_object_id,
        a_content_type,
        target_object_id,
        t_content_type,
        verb):
    if not verbs.apns_notification_dictionary.has_key(verb):
        return

    sender = User.objects.get(id=sender_id)
    receiver = User.objects.get(id=receiver_id).profile
    action_object = None
    target_object = None

    if action_object_id:
        action_object = \
                a_content_type.get_object_for_this_type(pk=action_object_id)
    if target_object_id:
        target_object = \
                t_content_type.get_object_for_this_type(pk=target_object_id)

    
    apns = ApnsMsg(
            sender,
            receiver.reg_token,
            action_object,
            target_object,
            verbs.apns_notification_dictionary[verb],
            receiver.is_ios())
    apns.format_alert_msg()
    apns.send()


class ApnsMsg(object):
    def __init__(self, sender, reg_token, action_object,
                 target_object, apns_args, is_ios):
        self.sender = sender
        self.reg_token = reg_token
        self.action_object = action_object
        self.target_object = target_object
        self.aps = dict(aps=apns_args.copy())
        self.is_ios = is_ios

    def format_alert_msg(self):
        alert_msg = self.aps['aps']['alert'].format(
                self.sender, 
                self.target_object,
                self.action_object)
        self.aps['aps']['alert'] = alert_msg

    def send(self):
        if self.is_ios:
            self.pushIOS()
        else:
            self.pushAndroid()

    def pushIOS(self):
	apns_notify(settings.APP_ID,
		    self.reg_token,
		    self.aps)

        return

    def pushAndroid(self):
	send_gcm_message(settings.GCM_API_KEY, 
			self.reg_token,
			self.aps)
        return


