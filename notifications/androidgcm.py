from pyfcm import FCMNotification
import logging


logger = logging.getLogger(__name__)


def send_gcm_message(key, reg_tokens, data):
    push_service = FCMNotification(api_key=key)
    message_title = data['title']
    message_body = data['body']

    result = push_service.notify_multiple_devices(registration_ids=reg_tokens, message_title=message_title, message_body=message_body)

    if result['failure'] == len(reg_tokens):
        return -1

    return 0


