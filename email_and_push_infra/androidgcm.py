from pyfcm import FCMNotification
#from gcm import GCM
import logging
import pdb

logger = logging.getLogger(__name__)


def send_gcm_message(key, reg_token, data):
	push_service = FCMNotification(api_key=key)
	
	# Your api-key can be gotten from:  https://console.firebase.google.com/project/<project-name>/settings/cloudmessaging
	
	registration_id = reg_token
	message_title = data['title']
	message_body = data['body']
	result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)

	#HACK HACK HACK - AnandR to fix it post event
	if type(result) is list:
		push_result = result[0]['success']
	elif type(result) is dict:
		push_result = result['success']
	else:
		push_result = -1
	
	if push_result > 0:
		logger.debug("Successfully sent notification for %s",reg_token)
	else:
		logger.debug("Remove reg_token %s", reg_token)



