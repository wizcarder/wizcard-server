import logging

from celery import task
from celery import shared_task
from wizserver import verbs
from pyapns import notify as apns_notify
from androidgcm import send_gcm_message
from django.conf import settings
from django.contrib.auth.models import User
import logging
from notifications.signals import notify
from notifications.models import BaseNotification
import pdb
from celery.utils.log import get_task_logger

from email_and_push_infra.models import EmailAndPush
from email_and_push_infra.html_gen_methods import HtmlGen



logger = logging.getLogger(__name__)




@shared_task(ignore_result=True)
def pushNotificationToApp(
        sender_id,
        receiver_id,
        action_object_id,
        a_content_type,
        target_object_id,
        t_content_type,
        notif_type,
        verb=None,
        fanout=False):

    action_object = None
    target_object = None

    if action_object_id:
        action_object = a_content_type.get_object_for_this_type(pk=action_object_id)
    if target_object_id:
        target_object = t_content_type.get_object_for_this_type(pk=target_object_id)

    if notif_type not in verbs.apns_notification_dictionary:
        return

    if not fanout:

        receiver_p = User.objects.get(id=receiver_id).profile
        app_user = receiver_p.app_user()
        if app_user.settings.dnd:
            return
        reg_tokens = [app_user.reg_token]

    else:
        users = target_object.get_wizcard_users()
        app_users = map(lambda x:x.profile.app_user(), users)
        reg_tokens = [au.regtoken for au in app_users if au.settings.dnd]

    apns_dict = verbs.apns_notification_dictionary[verb] if app_user.is_ios() else \
        verbs.gcm_notification_dictionary[notif_type]

    sender = User.objects.get(id=sender_id)

    apns = ApnsMsg(
        sender,
        reg_tokens,
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
        self.reg_tokens = reg_tokens
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

            alert_msg = self.message if self.message else self.aps['aps']['body'].format(self.sender,
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
        #TODO AR: Need to check if ios supports multiple recipients
        apns_notify(
            settings.APP_ID,
            self.reg_token,
            self.aps
        )
        return

    def pushAndroid(self):
        return send_gcm_message(settings.GCM_API_KEY,
                                self.reg_token,
                                self.aps['aps'])



@task(ignore_result=True)
def email_handler():
    logger.debug('Messaging Tick received')
    notifs = EmailAndPush.objects.unread_notifs(delivery_method=BaseNotification.EMAIL)
    for n in notifs:
        n.mark_as_read()
        if delivery_method == BaseNotification.EMAIL:
            emailer = HtmlGen(sender=n.actor, trigger=n.notif_type, target=n.target)
            #status = emailer.email_send()
            #n.update_status(status)





