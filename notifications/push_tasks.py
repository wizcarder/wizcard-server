__author__ = 'aammundi'

from pyapns import notify as apns_notify
from django.conf import settings
from notifications.androidgcm import send_gcm_message
from celery import shared_task


@shared_task(ignore_result=True)
def push_notification_to_app(notif_obj):

    # broadcast or targeted

    # if broadcast get iOS reg tokens and android reg_tokens for broadcast subsets

    # send push

    pass


class ApnsMsg(object):
    def __init__(self, sender, reg_tokens, action_object,
                 target_object, apns_args, message, device_type):
        self.sender = sender
        self.reg_tokens = reg_tokens
        self.action_object = action_object
        self.target_object = target_object
        self.aps = dict(aps=apns_args.copy())
        self.device_type = device_type
        self.message = message

    def format_alert_msg(self):
        if self.device_type == settings.DEVICE_IOS:
            alert_msg = self.aps['aps']['alert'].format(
                self.sender,
                self.target_object,
                self.action_object,
                self.message
            )
            self.aps['aps']['alert'] = alert_msg
        else:
            title = self.aps['aps']['title'].format(
                self.sender,
                self.target_object,
                self.action_object
            )

            alert_msg = self.message if self.message else \
                self.aps['aps']['body'].format(
                    self.sender,
                    self.target_object,
                    self.action_object,
                    self.message
                )

            self.aps['aps']['body'] = alert_msg
            self.aps['aps']['title'] = title

    def send(self):
        if self.device_type == settings.DEVICE_IOS:
            self.push_ios()
        elif self.device_type == settings.DEVICE_ANDROID:
            self.push_android()
        else:
            raise AssertionError("Invalid device type %s" % self.device_type)

    def push_ios(self):
        # TODO AR: Need to check if ios supports multiple recipients
        apns_notify(
            settings.APP_ID,
            self.reg_tokens,
            self.aps
        )
        return

    def push_android(self):
        return send_gcm_message(settings.GCM_API_KEY,
                                self.reg_tokens,
                                self.aps['aps'])
