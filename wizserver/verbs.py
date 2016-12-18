

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
MSG_CREATE_TABLE        = 17
MSG_JOIN_TABLE          = 18
MSG_LEAVE_TABLE         = 19
MSG_DESTROY_TABLE       = 20
MSG_TABLE_EDIT          = 21
MSG_TABLE_SUMMARY       = 22
MSG_TABLE_DETAILS       = 23
MSG_TABLE_QUERY         = 24
MSG_MY_TABLES           = 25
MSG_SETTINGS            = 26
MSG_OCR_SELF            = 27
MSG_OCR_DEAD_CARD       = 28
MSG_OCR_EDIT            = 29
MSG_EMAIL_TEMPLATE      = 30
MSG_GET_RECOMMENDATION  = 31
MSG_SET_RECO_ACTION     = 32
MSG_GET_COMMON_CONNECTIONS = 33
MSG_GET_VIDEO_THUMBNAIL = 34
MSG_MEISHI_START        = 35
MSG_MEISHI_FIND         = 36
MSG_MEISHI_END          = 37
MSG_FLICK               = 38
MSG_FLICK_ACCEPT        = 39
MSG_FLICK_ACCEPT_CONNECT = 40
MSG_FLICK_QUERY         = 41
MSG_MY_FLICKS           = 42
MSG_FLICK_WITHDRAW      = 44
MSG_FLICK_EDIT          = 45
MSG_FLICK_PICKS         = 46
MSG_WIZWEB_QUERY_USER   = 47
MSG_WIZWEB_QUERY_WIZCARD = 48
MSG_WIZWEB_CREATE_USER  = 49
MSG_WIZWEB_ADD_EDIT_CARD = 50

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
    'get_card_details'            : MSG_CARD_DETAILS,
    'query_tables'                : MSG_TABLE_QUERY,
    'my_tables'                   : MSG_MY_TABLES,
    'table_summary'               : MSG_TABLE_SUMMARY,
    'table_details'               : MSG_TABLE_DETAILS,
    'create_table'                : MSG_CREATE_TABLE,
    'join_table'                  : MSG_JOIN_TABLE,
    'leave_table'                 : MSG_LEAVE_TABLE,
    'destroy_table'               : MSG_DESTROY_TABLE,
    'table_edit'                  : MSG_TABLE_EDIT,
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
    'wizweb_query_user'           : MSG_WIZWEB_QUERY_USER,
    'wizweb_query_wizcard'	      : MSG_WIZWEB_QUERY_WIZCARD,
    'wizweb_create_user'	      : MSG_WIZWEB_CREATE_USER,
    'wizweb_add_edit_card'	      : MSG_WIZWEB_ADD_EDIT_CARD,
}


# notif Types
NOTIF_NULL          = 0
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
NOTIF_WIZWEB_UPDATE_WIZCARD     = 12
NOTIF_TABLE_INVITE              = 13
NOTIF_WIZCARD_FORWARD           = 14
NOTIF_TABLE_JOIN                = 15
NOTIF_TABLE_LEAVE               = 16
NOTIF_FOLLOW_EXPLICIT           = 17

# receiver types
WIZCARD_CONNECT_U   = 1
WIZCARD_CONNECT_T   = 2
WIZCARD_INVITE      = 3
EMAIL_INVITE        = 4
SMS_INVITE          = 5


INVITE_VERBS = {
    WIZCARD_CONNECT_U:'wiz_untrusted',
    WIZCARD_CONNECT_T: 'wiz_trusted',
    WIZCARD_INVITE: 'wizcard_invite',
    EMAIL_INVITE: 'email',
    SMS_INVITE: 'sms',
}

# Connection Staes
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
OWN = "own"
CONNECTED = "connected"
FOLLOWER = "follower"
FOLLOWER_D = "follower-d"
FOLLOWED = "followed"
OTHERS = "others"

    # (Verb, APNS_REQUIRED, APNS_TEXT)
WIZREQ_U = ('wizconnection request untrusted', 1)
WIZREQ_T = ('wizconnection request trusted', 1)
WIZREQ_T_HALF = ('wizconnection request trusted half', 0)
WIZREQ_F = ('wizconnection request follow', 1)
WIZCARD_ACCEPT = ('accepted wizcard', 1)
WIZCARD_REVOKE = ('revoked wizcard', 0)
WIZCARD_WITHDRAW_REQUEST = ('withdraw request', 0)
WIZCARD_DELETE = ('deleted wizcard', 0)
WIZCARD_TABLE_TIMEOUT = ('table timeout', 1)
WIZCARD_TABLE_DESTROY = ('table destroy', 1)
WIZCARD_UPDATE = ('wizcard update', 1)
WIZCARD_UPDATE_HALF = ('wizcard update half', 1)
WIZCARD_FLICK_TIMEOUT = ('flick timeout', 1)
WIZCARD_FLICK_PICK = ('flick pick', 1)
WIZCARD_TABLE_INVITE = ('table invite', 1)
WIZCARD_FORWARD = ('wizcard forward', 1)
WIZCARD_TABLE_JOIN = ('table join', 0)
WIZCARD_TABLE_LEAVE = ('table leave', 0)
WIZWEB_WIZCARD_UPDATE = ('wizweb wizcard update', 1)
WIZCARD_RECO_READY = ('new recommendations ready', 1)

apns_notification_dictionary = {
    WIZREQ_U[0]	: {
        'sound': 'flynn.caf',
        'badge': 0,
        #AA:TODO: separate verb from push message
        'alert': '{0.first_name} {0.last_name} would like to connect with you',
    },
    WIZREQ_F[0]	: {
        'sound': 'flynn.caf',
        'badge': 0,
        #AA:TODO: separate verb from push message
        'alert': '{0.first_name} {0.last_name} would like to follow you',
    },
    WIZREQ_T[0]	: {
        'sound': 'flynn.caf',
        'badge': 0,
        'alert': 'you have a new contact {0.first_name} {0.last_name}',
    },
    WIZCARD_ACCEPT[0]: {
        'sound': 'flynn.caf',
        'badge': 0,
        'alert': '{0.first_name} {0.last_name} accepted your invitation',
    },
    WIZCARD_TABLE_TIMEOUT[0]: {
        'sound': 'flynn.caf',
        'badge': 0,
        'alert': '{1.tablename} table has now expired',
    },
    WIZCARD_TABLE_DESTROY[0]: {
        'sound': 'flynn.caf',
        'badge': 0,
        'alert': '{0.first_name} {0.last_name}  deleted {1.tablename} table',
    },
    WIZCARD_UPDATE[0]: {
        'sound': 'flynn.caf',
        'badge': 0,
        'alert': '{0.first_name} {0.last_name} has an updated wizcard',
    },
    WIZCARD_UPDATE_HALF[0]: {
        'sound': 'flynn.caf',
        'badge': 0,
        'alert': '{0.first_name} {0.last_name} has an updated wizcard',
    },
    WIZCARD_FLICK_TIMEOUT[0]: {
        'sound': 'flynn.caf',
        'badge': 0,
        'alert': 'your flick has expired',
    },
    WIZCARD_FLICK_PICK[0]: {
        'sound': 'flynn.caf',
        'badge': 0,
        'alert': '{0.first_name} {0.last_name} picked up your flicked wizcard',
    },
    WIZWEB_WIZCARD_UPDATE[0]: {
        'sound': 'flynn.caf',
        'badge': 0,
        'alert': 'your wizcard was updated',
    },
    WIZCARD_RECO_READY[0]: {
        'sound': 'flynn.caf',
        'badge': 0,
        'alert': 'New Reco Ready',
    }
}

gcm_notification_dictionary = {
    WIZREQ_U[0]	: {
        'title':'Connection Request',
        #AA:TODO: separate verb from push message
        'body': '{0.first_name} {0.last_name} would like to connect with you',
    },
    WIZREQ_F[0]	: {
        'title':'Follow Request',
        #AA:TODO: separate verb from push message
        'body': '{0.first_name} {0.last_name} would like to follow you',
    },
    WIZREQ_T[0]	: {
        'title': 'Connected',
        'body': 'you have a new contact {0.first_name} {0.last_name}',
    },
    WIZCARD_ACCEPT[0]: {
        'title': 'Accepted',
        'body': '{0.first_name} {0.last_name} accepted your invitation',
    },

    WIZCARD_UPDATE[0]: {
        'title': 'Updated WizCard',
        'body': '{0.first_name} {0.last_name} has an updated wizcard',
    },
    WIZCARD_UPDATE_HALF[0]: {
        'title': 'Updated WizCard',
        'body': '{0.first_name} {0.last_name} has an updated wizcard',
    },
    WIZCARD_RECO_READY[0]: {
        'title' : 'New Recommendations Ready',
        'body': 'You have New Recommendations ready',
    }

}

