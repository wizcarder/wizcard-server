
NOTIF_NULL          = 0
ACCEPT_IMPLICIT     = 1
ACCEPT_EXPLICIT     = 2
DELETE_IMPLICIT     = 3
TABLE_TIMEOUT       = 4
UPDATE_WIZCARD      = 5
NEARBY_FLICKED_WIZCARD     = 6
NEARBY_USERS        = 7
NEARBY_TABLES       = 8
FLICK_TIMEOUT       = 9
FLICK_PICK          = 10
WITHDRAW_REQUEST    = 11
WIZWEB_UPDATE_WIZCARD = 12
TABLE_INVITE        = 13
WIZCARD_FORWARD     = 14
TABLE_JOIN          = 15
TABLE_LEAVE         = 16
FOLLOW_EXPLICIT     = 17

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
    SMS_INVITE: 'sms'
}

PENDING = 1
ACCEPTED = 2
DECLINED = 3
BLOCKED = 4
RELATIONSHIP_STATUSES = (
    (PENDING, 'Pending'),
    (ACCEPTED, 'Accepted'),
    (DECLINED, 'Declined'),
    (BLOCKED, 'Blocked'),
)

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
}

