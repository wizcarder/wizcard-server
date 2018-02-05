__author__ = 'aammundi'

from pyapns import notify as apns_notify
from django.conf import settings
from notifications.androidgcm import send_gcm_message
from celery import shared_task
from wizserver import verbs


@shared_task(ignore_result=True)
def push_notification_to_app(notif_obj, ntuple):

    # broadcast or targeted
    if verbs.get_notif_is_async(ntuple):
        flood_set = notif_obj.target.flood_set()
        # iOS
        reg_tokens = [x.profile.app_user().reg_token for x in flood_set if x.profile.app_user().device_type == settings.DEVICE_IOS]
        apns = ApnsMsg(
            notif_obj.actor,
            reg_tokens,
            notif_obj.action_object,
            notif_obj.target,
            verbs.get_apns_dict(notif_obj.notif_type, settings.DEVICE_IOS),
            verbs.get_notif_verb(ntuple),
            settings.DEVICE_IOS
        )

        apns.format_alert_msg()
        apns.send()

        # Android
        reg_tokens = [x.profile.app_user().reg_token for x in flood_set if x.profile.app_user().device_type == settings.DEVICE_ANDROID]
        apns = ApnsMsg(
            notif_obj.actor,
            reg_tokens,
            notif_obj.action_object,
            notif_obj.target,
            verbs.get_apns_dict(notif_obj.notif_type, settings.DEVICE_ANDROID),
            verbs.get_notif_verb(ntuple),
            settings.DEVICE_ANDROID
        )

        apns.format_alert_msg()
        apns.send()

    else:
        recipient = notif_obj.recipient.profile.app_user()
        reg_tokens = [recipient.reg_token]
        device_type = recipient.device_type

        apns = ApnsMsg(
            notif_obj.actor,
            reg_tokens,
            notif_obj.action_object,
            notif_obj.target,
            verbs.get_apns_dict(notif_obj.notif_type, device_type),
            verbs.get_notif_verb(ntuple),
            device_type
        )

        apns.format_alert_msg()
        apns.send()


class ApnsMsg(object):
    def __init__(self, sender, reg_tokens, action_object,
                 target_object, apns_args, message, device_type):
        self.sender = sender
        self.reg_tokens = reg_tokens
        self.action_object = action_object
        self.target_object = target_object
        self.aps = dict(aps=apns_args)
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
        return send_gcm_message(
            settings.GCM_API_KEY,
            self.reg_tokens,
            self.aps['aps']
        )
