from celery import shared_task
from celery.contrib import rdb
from celery import task
from wizserver import verbs
from pyapns import notify as apns_notify
from androidgcm import send_gcm_message
from django.conf import settings
from django.contrib.auth.models import User
from notifications.signals import notify
from notifications.models import Notification
import logging
import pdb

logger = logging.getLogger(__name__)


@task(ignore_result=True)
def create_notifs():

    # AR: TODO: Scaling challenge - Cannot have one task serially run through all notifications
    ns = Notification.objects.get_broadcast()

    for n in ns:
        users = n.target.get_wizcard_users()
        for u in users:
            notify.send(
                n.sender,
                u,
                notif_type=verbs.WIZCARD_ENTITY_BROADCAST[0],
                target=n.target,
                action_object=n.action_object,
                verb=n.verb,
            )
        n.mark_as_read()




@shared_task(ignore_result=True)
def pushNotificationToApp(
        sender_id,
        receiver_id,
        action_object_id,
        a_content_type,
        target_object_id,
        t_content_type,
        notif_type,
        verb=None):

    action_object = None
    target_object = None

    receiver_p = User.objects.get(id=receiver_id).profile
    app_user = receiver_p.app_user()

    if action_object_id:
        action_object = a_content_type.get_object_for_this_type(pk=action_object_id)
    if target_object_id:
        target_object = t_content_type.get_object_for_this_type(pk=target_object_id)

    if notif_type not in verbs.apns_notification_dictionary:
        return

    apns_dict = verbs.apns_notification_dictionary[verb] if app_user.is_ios() else \
        verbs.gcm_notification_dictionary[notif_type]

    sender = User.objects.get(id=sender_id)
    receiver_p = User.objects.get(id=receiver_id).profile
    app_user = receiver_p.app_user()

    if app_user.settings.dnd:
        return

    apns = ApnsMsg(
        sender,
        app_user.reg_token,
        action_object,
        target_object,
        apns_dict,
        verb,
        app_user.is_ios())

    apns.format_alert_msg()
    apns.send()


class ApnsMsg(object):
    def __init__(self, sender, reg_token, action_object,
                 target_object, apns_args, message, is_ios):
        self.sender = sender
        self.reg_token = reg_token
        self.action_object = action_object
        self.target_object = target_object
        self.aps = dict(aps=apns_args.copy())
        self.is_ios = is_ios
        self.message = message

    def format_alert_msg(self):
        if self.is_ios:
            alert_msg = self.aps['aps']['alert'].format(
                self.sender, 
                self.target_object,
                self.action_object,
                self.message
            )
            self.aps['aps']['alert'] = alert_msg
        else:
            title = self.aps['aps']['title'].format(self.sender,
                                                    self.target_object,
                                                    self.action_object
                                                    )
            alert_msg = self.aps['aps']['body'].format(
                self.sender,
                self.target_object,
                self.action_object,
                self.message
            )

            self.aps['aps']['body'] = alert_msg
            self.aps['aps']['title'] = title

    def send(self):
        if self.is_ios:
            self.pushIOS()
        else:
            self.pushAndroid()

    def pushIOS(self):
        apns_notify(
            settings.APP_ID,
            self.reg_token,
            self.aps
        )
        return

    def pushAndroid(self):
        send_gcm_message(
            settings.GCM_API_KEY,
            self.reg_token,
            self.aps['aps']
        )
        return
