__author__ = 'aammundi'

from pyapns import notify as apns_notify
from django.conf import settings
from notifications.androidgcm import send_gcm_message
from celery import task
from wizserver import verbs
from celery.contrib import rdb



@task(ignore_result=True)
def push_notification_to_app(notif_obj_pk, ntuple, flood_set=None):
    from notifications.models import SyncNotification, AsyncNotification
    notif_obj = SyncNotification.objects.get(id=notif_obj_pk)

    # broadcast or targeted
    if verbs.get_notif_is_async(ntuple):
        # iOS recipients
        reg_tokens = [x.profile.app_user().reg_token for x in flood_set if x.profile.app_user().device_type == settings.DEVICE_IOS]

        if reg_tokens:
            apns = ApnsMsg(
                notif_obj.actor,
                reg_tokens,
                notif_obj.action_object,
                notif_obj.target,
                verbs.get_apns_dict_for_device(notif_obj.notif_type, settings.DEVICE_IOS),
                settings.DEVICE_IOS,
                notif_obj.notification_text
            )

            apns.format_alert_msg()
            apns.send()

        # Android recipients
        reg_tokens = [x.profile.app_user().reg_token for x in flood_set if x.profile.app_user().device_type == settings.DEVICE_ANDROID]

        if reg_tokens:
            apns = ApnsMsg(
                notif_obj.actor,
                reg_tokens,
                notif_obj.action_object,
                notif_obj.target,
                verbs.get_apns_dict_for_device(notif_obj.notif_type, settings.DEVICE_ANDROID),
                settings.DEVICE_ANDROID,
                notif_obj.notification_text
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
            verbs.get_apns_dict_for_device(notif_obj.notif_type, device_type),
            device_type,
        )

        apns.format_alert_msg()
        apns.send()


class ApnsMsg(object):
    def __init__(self, sender, reg_tokens, action_object,
                 target_object, apns_args, device_type, custom_message=""):
        self.sender = sender
        self.reg_tokens = reg_tokens
        self.action_object = action_object
        self.target_object = target_object
        self.aps = dict(aps=apns_args)
        self.device_type = device_type
        self.message = custom_message

    def format_alert_msg(self):
        if self.device_type == settings.DEVICE_IOS:
            alert_msg = self.message if self.message else \
                self.aps['aps']['alert'].format(
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
