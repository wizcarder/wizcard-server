OK = {'errno':0, 'Description': ""}
NONE_FOUND = {'errno': 1, 'str': "Query returned no results"}
EXISTING_MEMBER = {'errno': 2, 'str': "already joined table"}
INVALID_USERNAME_PASSWORD = {'errno': 3, 'str': "invalid username or password"}
AUTHENTICATION_FAILED = {'errno': 4, 'str': "authentication failed"}
USER_DOESNT_EXIST = {'errno': 5, 'str': "user doesn't exist"}
TABLE_DOESNT_EXIST = {'errno': 6, 'str': "table doesn't exist"}
OBJECT_DOESNT_EXIST = {'errno': 7, 'str': "sorry, we couldn't complete your request"}
LOCATION_UNKNOWN = {'errno': 8, 'str': "location error"}
INTERNAL_ERROR = {'errno': 9, 'str': "internal error"}
EXISTING_CONNECTION = {'errno': 10, 'str': "your request is pending"}
PENDING_CONNECTION = {'errno': 11, 'str': "pending connection"}
INVALID_MESSAGE = {'errno': 12, 'str': "invalid message"}
NOT_AUTHORIZED = {'errno': 13, 'str': "user is not authorized"}
NAME_ERROR = {'errno': 14, 'str': "invalid table details"}
PHONE_CHECK_RETRY_EXCEEDED = {'errno': 15, 'str': "too many attempts...do you want to continue with a new code ?"}
PHONE_CHECK_CHALLENGE_RESPONSE_DENIED = {'errno': 16, 'str': "keys do not match"}
PHONE_CHECK_CHALLENGE_RESPONSE_INVALID_DEVICE = {'errno': 17, 'str': "unauthorized device"}
PHONE_CHECK_TIMEOUT_EXCEEDED = {'errno': 18, 'str': "you have exceeded the timeout"}
NEXMO_SMS_SEND_FAILED = {'errno': 19, 'str': "SMS send failed"}
VALIDITY_CHECK_FAILED = {'errno': 20, 'str': "validity check fails on data"}
CRITICAL_ERROR = {'errno': 21, 'str': "something went wrong...please delete and reinstall the app"}
LIB_OCR_ERROR = {'errno': 22, 'str': "OCR lib error"}
LIB_OCR_CELERY_TIMEOUT = {'errno': 23, 'str': "OCR response delayed"}

# 24, 25 should not be changed...ever.
VERSION_UPGRADE = {'errno': 24, 'str': "We have a better version of WizCard, Upgrade to Continue"}
REVERSE_INVITE = {'errno': 25, 'str': "Invitation expired/revoked, Do you want to invite?"}

NO_RECEIVER = {'errno': 26, 'str': "No receiver in the request"}
INVALID_STATE = {'errno': 27, 'str': "Invalid connection state"}
SELF_INVITE = {'errno': 28, 'str': "Connecting with Yourself - You are well connected;)"}
EMBED_FAILED = {'errno': 29, 'str': "Couldn't Embed Video"}
POLL_ID_INVALID = {'errno': 30, 'str': "sorry, we couldn't find this poll"}
POLL_RESPONSE_INVALID_QUESTION = {'errno': 31, 'str': "sorry, we couldn't find this poll question"}
POLL_RESPONSE_INVALID_ANSWER = {'errno': 32, 'str': "sorry, this answer choice is invalid"}
SCAN_USER_AUTH_ERROR = {'errno': 33, 'str': "Couldn't find active campaign to attach lead scan"}
ENTITY_DELETED = {'errno': 34, 'str': "sorry, this event is no longer active"}



IGNORE = {'result': 1, 'ignore': 1, 'errStr': ""}
