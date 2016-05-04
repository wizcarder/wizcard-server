import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from wizcard.settings import PHONE_CHECK_MESSAGE
from lib.nexmomessage import NexmoMessage
import logging
logger = logging.getLogger(__name__)


TEST_NUMBER = 14084641727
#RESPONSE_MODE = "voice"
RESPONSE_MODE = "sms"

msg = PHONE_CHECK_MESSAGE.copy()
msg['to'] = TEST_NUMBER
msg['text'] = "Hello WizCarder"


if RESPONSE_MODE == "voice":
    msg['servicetype'] = "tts"
elif RESPONSE_MODE == "sms":
    msg['servicetype'] = "sms"

sms = NexmoMessage(msg)
sms.set_text_info(msg['text'])
response = sms.send_request()
print response
