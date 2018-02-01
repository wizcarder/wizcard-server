from django.conf import settings


# All message types
MSG_LOGIN               = 1
MSG_PHONE_CHECK_REQ     = 2
MSG_PHONE_CHECK_RESP    = 3
MSG_REGISTER            = 4
MSG_CONTACTS_UPLOAD     = 5
MSG_NOTIFICATIONS_GET   = 6
MSG_CURRENT_LOCATION    = 7
MSG_WIZCARD_EDIT        = 8
MSG_SEND_ASSET_XYZ      = 9
MSG_WIZCARD_ACCEPT      = 10
MSG_WIZCARD_DECLINE     = 11
MSG_ROLODEX_DELETE      = 12
MSG_ROLODEX_EDIT        = 13
MSG_ARCHIVED_CARDS      = 14
MSG_CARD_DETAILS        = 15
MSG_QUERY_USER          = 16
MSG_ENTITY_CREATE       = 17
MSG_ENTITY_DESTROY      = 18
MSG_ENTITY_EDIT         = 19
MSG_ENTITY_JOIN         = 20
MSG_ENTITY_LEAVE        = 21
MSG_ENTITY_SUMMARY      = 22
MSG_ENTITY_DETAILS      = 23
MSG_ENTITY_QUERY        = 24
MSG_MY_ENTITIES         = 25
MSG_GET_EVENTS          = 26
MSG_ENTITIES_ENGAGE     = 28
MSG_SETTINGS            = 29
MSG_OCR_SELF            = 30
MSG_OCR_DEAD_CARD       = 31
MSG_OCR_EDIT            = 32
MSG_EMAIL_TEMPLATE      = 33
MSG_GET_RECOMMENDATION  = 34
MSG_SET_RECO_ACTION     = 35
MSG_GET_COMMON_CONNECTIONS = 36
MSG_GET_VIDEO_THUMBNAIL = 37
MSG_POLL_RESPONSE       = 38
MSG_MEISHI_START        = 39
MSG_MEISHI_FIND         = 40
MSG_MEISHI_END          = 41
MSG_FLICK               = 42
MSG_FLICK_ACCEPT        = 43
MSG_FLICK_ACCEPT_CONNECT = 44
MSG_FLICK_QUERY         = 45
MSG_MY_FLICKS           = 46
MSG_FLICK_WITHDRAW      = 47
MSG_FLICK_EDIT          = 48
MSG_FLICK_PICKS         = 49
MSG_LEAD_SCAN           = 50


wizcardMsgTypes = {
    'login'                       : MSG_LOGIN,
    'phone_check_req'             : MSG_PHONE_CHECK_REQ,
    'phone_check_rsp'             : MSG_PHONE_CHECK_RESP,
    'register'                    : MSG_REGISTER,
    'current_location'            : MSG_CURRENT_LOCATION,
    'contacts_upload'             : MSG_CONTACTS_UPLOAD,
    'get_cards'                   : MSG_NOTIFICATIONS_GET,
    'edit_card'                   : MSG_WIZCARD_EDIT,
    'edit_rolodex_card'           : MSG_ROLODEX_EDIT,
    'accept_connection_request'   : MSG_WIZCARD_ACCEPT,
    'decline_connection_request'  : MSG_WIZCARD_DECLINE,
    'delete_rolodex_card'         : MSG_ROLODEX_DELETE,
    'archived_cards'              : MSG_ARCHIVED_CARDS,
    'card_flick'                  : MSG_FLICK,
    'card_flick_accept'           : MSG_FLICK_ACCEPT,
    'card_flick_accept_connect'   : MSG_FLICK_ACCEPT_CONNECT,
    'my_flicks'                   : MSG_MY_FLICKS,
    'flick_withdraw'              : MSG_FLICK_WITHDRAW,
    'flick_edit'                  : MSG_FLICK_EDIT,
    'query_flicks'                : MSG_FLICK_QUERY,
    'flick_pickers'               : MSG_FLICK_PICKS,
    'send_asset_to_xyz'           : MSG_SEND_ASSET_XYZ,
    'send_query_user'             : MSG_QUERY_USER,
    'entity_create'               : MSG_ENTITY_CREATE,
    'entity_destroy'              : MSG_ENTITY_DESTROY,
    'entity_edit'                 : MSG_ENTITY_EDIT,
    'entity_join'                 : MSG_ENTITY_JOIN,
    'entity_leave'                : MSG_ENTITY_LEAVE,
    'entity_summary'              : MSG_ENTITY_SUMMARY,
    'entity_details'              : MSG_ENTITY_DETAILS,
    'entity_query'                : MSG_ENTITY_QUERY,
    'my_entities'                 : MSG_MY_ENTITIES,
    'get_events'                  : MSG_GET_EVENTS,
    'entities_like'               : MSG_ENTITIES_ENGAGE,
    'get_card_details'            : MSG_CARD_DETAILS,
    'settings'                    : MSG_SETTINGS,
    'ocr_req_self'                : MSG_OCR_SELF,
    'ocr_req_dead_card'           : MSG_OCR_DEAD_CARD,
    'ocr_dead_card_edit'          : MSG_OCR_EDIT,
    'meishi_start'                : MSG_MEISHI_START,
    'meishi_find'                 : MSG_MEISHI_FIND,
    'meishi_end'                  : MSG_MEISHI_END,
    'get_email_template'          : MSG_EMAIL_TEMPLATE,
    'get_recommendations'         : MSG_GET_RECOMMENDATION,
    'set_reco_action'             : MSG_SET_RECO_ACTION,
    'get_common_connections'      : MSG_GET_COMMON_CONNECTIONS,
    'get_video_thumbnail'         : MSG_GET_VIDEO_THUMBNAIL,
    'poll_response'               : MSG_POLL_RESPONSE,
    'lead_scan'                   : MSG_LEAD_SCAN
}


# notif Types
NOTIF_NULL                      = 0
NOTIF_ACCEPT_IMPLICIT           = 1
NOTIF_ACCEPT_EXPLICIT           = 2
NOTIF_DELETE_IMPLICIT           = 3
NOTIF_TABLE_TIMEOUT             = 4
NOTIF_UPDATE_WIZCARD            = 5
NOTIF_NEARBY_FLICKED_WIZCARD    = 6
NOTIF_NEARBY_USERS              = 7
NOTIF_NEARBY_TABLES             = 8
NOTIF_FLICK_TIMEOUT             = 9
NOTIF_FLICK_PICK                = 10
NOTIF_WITHDRAW_REQUEST          = 11
NOTIF_TABLE_INVITE              = 12
NOTIF_WIZCARD_FORWARD           = 13
NOTIF_ENTITY_JOIN               = 14
NOTIF_ENTITY_LEAVE              = 15
NOTIF_FOLLOW_EXPLICIT           = 16
NOTIF_ENTITY_UPDATE             = 17
NOTIF_ENTITY_EXPIRE             = 18
NOTIF_ENTITY_DELETE             = 19
NOTIF_ENTITY_CREATE             = 20
NOTIF_NEW_RECO                  = 21
NOTIF_NEW_WIZUSER               = 22
NOTIF_ENTITY_BROADCAST          = 23
NOTIF_SCANNED_USER              = 24
NOTIF_INVITE_USER               = 25
NOTIF_ENTITY_REMINDER           = 26
NOTIF_INVITE_EXHIBITOR          = 27
NOTIF_INVITE_ATTENDEE           = 28


# receiver types
WIZCARD_CONNECT_U   = 1
WIZCARD_CONNECT_T   = 2
WIZCARD_INVITE      = 3
EMAIL_INVITE        = 4
SMS_INVITE          = 5


INVITE_VERBS = {
    WIZCARD_CONNECT_U: 'wiz_untrusted',
    WIZCARD_CONNECT_T: 'wiz_trusted',
    WIZCARD_INVITE: 'wizcard_invite',
    EMAIL_INVITE: 'email',
    SMS_INVITE: 'sms',
}

# Connection States
PENDING = 1
ACCEPTED = 2
DECLINED = 3
DELETED = 4
BLOCKED = 5

RELATIONSHIP_STATUSES = (
    (PENDING, 'Pending'),
    (ACCEPTED, 'Accepted'),
    (DECLINED, 'Declined'),
    (DELETED, 'Deleted'),
    (BLOCKED, 'Blocked'),
)

# tags
ADMIN = "admin"
OWN = "own"
CONNECTED = "connected"
FOLLOWER = "follower"
FOLLOWER_D = "follower-d"
FOLLOWED = "followed"
OTHERS = "others"

# (NotifType, Verb, APNS_REQUIRED, IS_ASYNC)
# Intentionally indenting this way notwithstanding the PEP warning, to improve readability

def get_notif_type(tuple):
    return tuple[0]

def get_notif_verb(tuple):
    return tuple[1]

def get_notif_apns_required(tuple):
    return tuple[2]

def get_notif_is_async(tuple):
    return tuple[3]


WIZCARD_NULL                = (NOTIF_NULL, "Empty notif", False, False)
WIZREQ_U                    = (NOTIF_ACCEPT_EXPLICIT, 'wizconnection request untrusted', True, False)
WIZREQ_T                    = (NOTIF_ACCEPT_IMPLICIT, 'wizconnection request trusted', True, False)
WIZREQ_T_HALF               = (NOTIF_ACCEPT_IMPLICIT, 'wizconnection request trusted half', False, False)
WIZREQ_F                    = (NOTIF_FOLLOW_EXPLICIT, 'wizconnection request follow', True, False)
WIZCARD_ACCEPT              = (NOTIF_ACCEPT_EXPLICIT, 'accepted wizcard', True, False)
WIZCARD_REVOKE              = (NOTIF_DELETE_IMPLICIT, 'revoked wizcard', 0)
WIZCARD_WITHDRAW_REQUEST    = (NOTIF_WITHDRAW_REQUEST, 'withdraw request', 0)
WIZCARD_DELETE              = (NOTIF_DELETE_IMPLICIT, 'deleted wizcard', 0)
WIZCARD_TABLE_TIMEOUT       = (NOTIF_TABLE_TIMEOUT, 'table timeout', True, True)
WIZCARD_TABLE_DESTROY       = (NOTIF_TABLE_TIMEOUT, 'table destroy', True, True)
WIZCARD_UPDATE              = (NOTIF_UPDATE_WIZCARD, 'wizcard update', True, False)
WIZCARD_UPDATE_HALF         = (NOTIF_UPDATE_WIZCARD, 'wizcard update half', True, False)
WIZCARD_FLICK_TIMEOUT       = (NOTIF_FLICK_TIMEOUT, 'flick timeout', True, False)
WIZCARD_FLICK_PICK          = (NOTIF_FLICK_PICK, 'flick pick', True, False)
WIZCARD_TABLE_INVITE        = (NOTIF_TABLE_INVITE, 'table invite', True, False)
WIZCARD_FORWARD             = (NOTIF_WIZCARD_FORWARD, 'wizcard forward', True, False)
WIZCARD_ENTITY_JOIN         = (NOTIF_ENTITY_JOIN, 'entity join', False, True)
WIZCARD_ENTITY_LEAVE        = (NOTIF_ENTITY_LEAVE, 'entity leave', 0)
WIZCARD_RECO_READY          = (NOTIF_NEW_RECO, 'new recommendations ready', 1)
WIZCARD_ENTITY_UPDATE       = (NOTIF_ENTITY_UPDATE, 'event_updated', 0)
WIZCARD_ENTITY_EXPIRE       = (NOTIF_ENTITY_EXPIRE, 'event_expired', 0)
WIZCARD_ENTITY_DELETE       = (NOTIF_ENTITY_DELETE, 'event_deleted', 0)
WIZCARD_EVENT_REMINDER      = (NOTIF_ENTITY_REMINDER, 'event_reminder', 1)
WIZCARD_NEW_USER            = (NOTIF_NEW_WIZUSER, 'new_user', 0)
WIZCARD_SCANNED_USER        = (NOTIF_SCANNED_USER, 'scanned_user', 0)
WIZCARD_INVITE_USER         = (NOTIF_INVITE_USER, 'invite_user', 0)
WIZCARD_INVITE_EXHIBITOR    = (NOTIF_INVITE_EXHIBITOR, 'invite_exhibitor', 0)
WIZCARD_INVITE_ATTENDEE     = (NOTIF_INVITE_ATTENDEE, 'invite_attendee', 0)
WIZCARD_ENTITY_BROADCAST    = (NOTIF_ENTITY_BROADCAST, 'event broadcast', 1)


# notify.send sends the whole tuple. Thus for serializer path, we need a mapping
# from the integer notif_type to tuple. Not all mappings are required, adding in
# here as needed

notif_type_tuple_dict = {
    NOTIF_ENTITY_BROADCAST: WIZCARD_ENTITY_BROADCAST
}

apns_notification_dictionary = {
    WIZREQ_U[0]	: {
        'sound': 'flynn.caf',
        'badge': 0,
        'title': 'Connection Request',
        'alert': '{0.first_name} {0.last_name} would like to connect with you',
    },
    WIZREQ_F[0]	: {
        'sound': 'flynn.caf',
        'badge': 0,
        'title': 'Follow Request',
        'alert': '{0.first_name} {0.last_name} would like to follow you',
    },
    WIZREQ_T[0]	: {
        'sound': 'flynn.caf',
        'badge': 0,
        'title': 'Connected',
        'alert': 'you have a new contact {0.first_name} {0.last_name}',
    },
    WIZCARD_ACCEPT[0]: {
        'sound': 'flynn.caf',
        'badge': 0,
        'title': 'Accepted',
        'alert': '{0.first_name} {0.last_name} accepted your invitation',
    },
    WIZCARD_TABLE_TIMEOUT[0]: {
        'sound': 'flynn.caf',
        'badge': 0,
        'title': 'Wizcard - Table expired',
        'alert': '{1.name} table has now expired',
    },
    WIZCARD_TABLE_DESTROY[0]: {
        'sound': 'flynn.caf',
        'badge': 0,
        'title': 'Wizcard - Table deleted',
        'alert': '{0.first_name} {0.last_name}  deleted {1.tablename} table',
    },
    WIZCARD_UPDATE[0]: {
        'sound': 'flynn.caf',
        'badge': 0,
        'title': 'Updated WizCard',
        'alert': '{0.first_name} {0.last_name} has an updated wizcard',
    },
    WIZCARD_UPDATE_HALF[0]: {
        'sound': 'flynn.caf',
        'badge': 0,
        'title': 'Updated WizCard',
        'alert': '{0.first_name} {0.last_name} has an updated wizcard',
    },
    WIZCARD_RECO_READY[0]: {
        'sound': 'flynn.caf',
        'badge': 0,
        'title': 'Wizcard - New Recommendations waiting for you',
        'alert': 'New Recommendations',
    },
    WIZCARD_ENTITY_BROADCAST[0]: {
        'sound': 'flynn.caf',
        'badge': 0,
        'title': 'Event announcement',
        'alert': 'Message from {1.name} - {3}'
    },
}

def get_apns_dict(verb, device_type):
    if device_type == settings.DEVICE_IOS:
        push_dict = {key: value for key, value in apns_notification_dictionary[verb] if key in ['sound', 'badge', 'alert']}
    elif device_type == settings.DEVICE_ANDROID:
        push_dict = {key: value for key, value in apns_notification_dictionary[verb] if key in ['title', 'alert']}
        # small adjustment for key name for android
        push_dict['body']=push_dict.pop('alert')
    else:
        raise AssertionError("invalid device_type %s" % device_type)

    return push_dict

