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
MSG_ENTITY_ACCESS       = 20
MSG_ENTITY_SUMMARY      = 21
MSG_ENTITY_DETAILS      = 22
MSG_ENTITY_QUERY        = 23
MSG_MY_ENTITIES         = 24
MSG_GET_EVENTS          = 25
MSG_ENTITIES_ENGAGE     = 26
MSG_SETTINGS            = 27
MSG_OCR_SELF            = 28
MSG_OCR_DEAD_CARD       = 29
MSG_OCR_EDIT            = 30
MSG_EMAIL_TEMPLATE      = 31
MSG_GET_RECOMMENDATION  = 32
MSG_SET_RECO_ACTION     = 33
MSG_GET_COMMON_CONNECTIONS = 34
MSG_GET_VIDEO_THUMBNAIL = 35
MSG_POLL_RESPONSE       = 36
MSG_MEISHI_START        = 37
MSG_MEISHI_FIND         = 38
MSG_MEISHI_END          = 39
MSG_FLICK               = 40
MSG_FLICK_ACCEPT        = 41
MSG_FLICK_ACCEPT_CONNECT = 42
MSG_FLICK_QUERY         = 43
MSG_MY_FLICKS           = 44
MSG_FLICK_WITHDRAW      = 45
MSG_FLICK_EDIT          = 46
MSG_FLICK_PICKS         = 47
MSG_LEAD_SCAN           = 48


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
    'entity_access'               : MSG_ENTITY_ACCESS,
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
    'lead_scan'                   : MSG_LEAD_SCAN,
}


# notif Types
NOTIF_NULL                      = 0
NOTIF_ACCEPT_IMPLICIT           = 1
NOTIF_ACCEPT_EXPLICIT           = 2
NOTIF_DELETE_IMPLICIT           = 3
NOTIF_ACCEPT_IMPLICIT_H         = 4

NOTIF_UPDATE_WIZCARD_H          = 5
NOTIF_UPDATE_WIZCARD_F          = 6
NOTIF_NEARBY_USERS              = 7
NOTIF_NEARBY_TABLES             = 8

NOTIF_NEARBY_FLICKED_WIZCARDS   = 9
NOTIF_FLICK_TIMEOUT             = 10
NOTIF_FLICK_PICK                = 11
NOTIF_WITHDRAW_REQUEST          = 12
NOTIF_TABLE_INVITE              = 13
NOTIF_WIZCARD_FORWARD           = 14

NOTIF_ENTITY_JOIN               = 15
NOTIF_ENTITY_LEAVE              = 16

NOTIF_ENTITY_UPDATE             = 18
NOTIF_ENTITY_EXPIRE             = 19
NOTIF_ENTITY_DELETE             = 20
NOTIF_ENTITY_CREATE             = 21
NOTIF_NEW_RECO                  = 22
NOTIF_NEW_WIZUSER               = 23
NOTIF_ENTITY_BROADCAST          = 24
NOTIF_SCANNED_USER              = 25
NOTIF_INVITE_USER               = 26
NOTIF_ENTITY_REMINDER           = 27
NOTIF_INVITE_EXHIBITOR          = 28
NOTIF_INVITE_ATTENDEE           = 29

NOTIF_OPERATION_CREATE = 'C'
NOTIF_OPERATION_DELETE = 'D'


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


WIZCARD_NULL                = (NOTIF_NULL, "Empty notif", False, False)
WIZREQ_U                    = (NOTIF_ACCEPT_EXPLICIT, 'wizconnection request untrusted', True, False)
WIZREQ_T                    = (NOTIF_ACCEPT_IMPLICIT, 'wizconnection request trusted', True, False)
WIZREQ_T_HALF               = (NOTIF_ACCEPT_IMPLICIT_H, 'wizconnection request trusted half', False, False)
WIZCARD_ACCEPT              = (NOTIF_ACCEPT_EXPLICIT, 'accepted wizcard', True, False)
WIZCARD_REVOKE              = (NOTIF_DELETE_IMPLICIT, 'revoked wizcard', False, False)
WIZCARD_WITHDRAW_REQUEST    = (NOTIF_WITHDRAW_REQUEST, 'withdraw request', False, False)
WIZCARD_DELETE              = (NOTIF_DELETE_IMPLICIT, 'deleted wizcard', False, False)
WIZCARD_UPDATE_FULL         = (NOTIF_UPDATE_WIZCARD_F, 'wizcard update', True, True)
WIZCARD_UPDATE_HALF         = (NOTIF_UPDATE_WIZCARD_H, 'wizcard update half', False, True)
WIZCARD_FLICK_TIMEOUT       = (NOTIF_FLICK_TIMEOUT, 'flick timeout', True, False)
WIZCARD_FLICK_PICK          = (NOTIF_FLICK_PICK, 'flick pick', True, False)
WIZCARD_TABLE_INVITE        = (NOTIF_TABLE_INVITE, 'table invite', True, False)
WIZCARD_FORWARD             = (NOTIF_WIZCARD_FORWARD, 'wizcard forward', True, False)
WIZCARD_ENTITY_ATTACH       = (NOTIF_ENTITY_JOIN, 'entity join', False, True)
WIZCARD_ENTITY_DETACH       = (NOTIF_ENTITY_LEAVE, 'entity leave', False, True)
WIZCARD_RECO_READY          = (NOTIF_NEW_RECO, 'new recommendations ready', True, False)
WIZCARD_ENTITY_UPDATE       = (NOTIF_ENTITY_UPDATE, 'event_updated', True, True)
WIZCARD_ENTITY_EXPIRE       = (NOTIF_ENTITY_EXPIRE, 'event_expired', False, True)
WIZCARD_ENTITY_DELETE       = (NOTIF_ENTITY_DELETE, 'event_deleted', False, True)
WIZCARD_EVENT_REMINDER      = (NOTIF_ENTITY_REMINDER, 'event_reminder', True, True)
WIZCARD_NEW_USER            = (NOTIF_NEW_WIZUSER, 'new_user', False, True)
WIZCARD_SCANNED_USER        = (NOTIF_SCANNED_USER, 'scanned_user', False, True)
WIZCARD_INVITE_USER         = (NOTIF_INVITE_USER, 'invite_user', False, True)
WIZCARD_INVITE_EXHIBITOR    = (NOTIF_INVITE_EXHIBITOR, 'invite_exhibitor', False, True)
WIZCARD_INVITE_ATTENDEE     = (NOTIF_INVITE_ATTENDEE, 'invite_attendee', False, True)
WIZCARD_ENTITY_BROADCAST    = (NOTIF_ENTITY_BROADCAST, 'event broadcast', True, True)

def get_notif_type(ntuple):
    return ntuple[0]

def get_notif_verb(ntuple):
    return ntuple[1]

def get_notif_apns_required(ntuple):
    return ntuple[2]

def get_notif_is_async(ntuple):
    return ntuple[3]


# reverse mapping from notif_type to tuple. All Async types will need this mapping
# notif model stores the denormalized values. We need tuple for push business logic
# in the handler. Add as needed

notif_type_tuple_dict = {
    NOTIF_UPDATE_WIZCARD_H: WIZCARD_UPDATE_HALF,
    NOTIF_UPDATE_WIZCARD_F: WIZCARD_UPDATE_FULL,
    NOTIF_ENTITY_JOIN: WIZCARD_ENTITY_ATTACH,
    NOTIF_ENTITY_LEAVE: WIZCARD_ENTITY_DETACH,
    NOTIF_ENTITY_UPDATE: WIZCARD_ENTITY_UPDATE,
    NOTIF_ENTITY_EXPIRE: WIZCARD_ENTITY_EXPIRE,
    NOTIF_ENTITY_DELETE: WIZCARD_ENTITY_DELETE,
    NOTIF_ENTITY_BROADCAST: WIZCARD_ENTITY_BROADCAST,
}

EMAIL_TEMPLATE_MAPPINGS = {
    NOTIF_NEW_WIZUSER: {"template": "welcome.html", "subject": "Welcome %s to WizCard"},
    NOTIF_SCANNED_USER: {"template": "emailwizcard.html", "subject": "%s has scanned your card on WizCard"},
    NOTIF_INVITE_ATTENDEE: {"template": "invite_attendee.html", "subject": "%s - has invited you to Create your Campaign"},
    NOTIF_INVITE_EXHIBITOR: {"template": "invite_exhibitor.html", "subject": "%s - Welcome to %s"},
    NOTIF_INVITE_USER: {"template": "emailwizcard.html", "subject": "%s has invited you to Connect on WizCard"},
}


apns_notification_dictionary = {
    get_notif_type(WIZREQ_U)	: {
        'sound': 'flynn.caf',
        'badge': 0,
        'title': 'Connection Request',
        'message': '{0.first_name} {0.last_name} would like to connect with you',
    },
    get_notif_type(WIZREQ_T)	: {
        'sound': 'flynn.caf',
        'badge': 0,
        'title': 'Connected',
        'message': 'you have a new contact {0.first_name} {0.last_name}',
    },
    get_notif_type(WIZCARD_ACCEPT): {
        'sound': 'flynn.caf',
        'badge': 0,
        'title': 'Accepted',
        'message': '{0.first_name} {0.last_name} accepted your invitation',
    },
    get_notif_type(WIZCARD_ENTITY_UPDATE): {
        'sound': 'flynn.caf',
        'badge': 0,
        'title': 'Event Updated',
        'message': 'Event {1.name} has an update',
    },
    get_notif_type(WIZCARD_ENTITY_EXPIRE): {
        'sound': 'flynn.caf',
        'badge': 0,
        'title': 'Wizcard - expired',
        'message': '{1.name} has now expired',
    },
    get_notif_type(WIZCARD_ENTITY_DELETE): {
        'sound': 'flynn.caf',
        'badge': 0,
        'title': 'Wizcard -  Deleted',
        'message': '{0.first_name} {0.last_name}  deleted {1.tablename}',
    },
    get_notif_type(WIZCARD_UPDATE_FULL): {
        'sound': 'flynn.caf',
        'badge': 0,
        'title': 'Updated WizCard',
        'message': '{0.first_name} {0.last_name} has an updated wizcard',
    },
    get_notif_type(WIZCARD_RECO_READY): {
        'sound': 'flynn.caf',
        'badge': 0,
        'title': 'Wizcard - New Recommendations waiting for you',
        'message': 'New Recommendations',
    },
    get_notif_type(WIZCARD_ENTITY_BROADCAST): {
        'sound': 'flynn.caf',
        'badge': 0,
        'title': 'Event announcement',
        'message': 'Message from {1.name} - {3}'
    },
}

def get_apns_dict(notif_type):
    if notif_type not in apns_notification_dictionary:
        raise AssertionError("Add notifType %s to apns_dict" % notif_type)

    return apns_notification_dictionary[notif_type]

def get_apns_dict_for_device(notif_type, device_type):
    push_dict = get_apns_dict(notif_type)

    if device_type == settings.DEVICE_IOS:
        push_dict = {k: v for (k, v) in push_dict.items() if k in ['sound', 'badge', 'message']}
        # adjustment for key name per device_type
        push_dict['alert'] = push_dict.pop('message')
    elif device_type == settings.DEVICE_ANDROID:
        push_dict = {k: v for (k, v) in push_dict.items() if k in ['title', 'message']}
        push_dict['body'] = push_dict.pop('message')
    else:
        raise AssertionError("invalid device_type %s" % device_type)

    return push_dict

