from celery import task
from celery.contrib import rdb
from wizserver import verbs
from pyapns import notify as apns_notify
from pyapns import configure, provision, feedback
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@task(ignore_result=True)
def pushNotificationToApp(notif):
    if not verbs.apns_notification_dictionary.has_key(notif.verb):
        return

    apns = ApnsMsg(
            notif.recipient,
            notif.actor,
            notif.target,
            verbs.apns_notification_dictionary[notif.verb])
    apns.format_alert_msg()
    apns.send()


class ApnsMsg(object):
    def __init__(self, receiver, sender, object, apns_args):
        self.sender = sender
        self.receiver = receiver
        self.r_profile = receiver.profile
        self.object = object 
        self.reg_token = self.r_profile.reg_token
        self.aps = dict(aps=apns_args)

    def format_alert_msg(self):
        alert_msg = self.aps['aps']['alert'].format(self.sender, 
                                                    self.object)
        self.aps['aps']['alert'] = alert_msg

    def send(self):
        if self.r_profile.is_ios():
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


