
    # (Verb, APNS_REQUIRED, APNS_TEXT)
WIZREQ_U = ('wizconnection request untrusted', 1, 'xxx would like to connect with you')
WIZREQ_T = ('wizconnection request trusted', 1, 'you have a new contact')
WIZCARD_ACCEPT = ('accepted wizcard', 1, 'xxx accepted your invitation')
WIZCARD_REVOKE = ('revoked wizcard', 0)
WIZCARD_WITHDRAW_REQUEST = ('withdraw request', 0)
WIZCARD_DELETE = ('deleted wizcard', 0)
WIZCARD_TABLE_TIMEOUT = ('table timeout', 1, 'xxx table has now expired')
WIZCARD_TABLE_DESTROY = ('table destroy', 1, 'xxx deleted yyy table')
WIZCARD_UPDATE = ('wizcard update', 1, 'xxx has an updated wizcard')
WIZCARD_FLICK_TIMEOUT = ('flick timeout', 1, 'your flick has expired')
WIZCARD_FLICK_PICK = ('flick pick', 1, 'yy picked up your flicked wizcard')
WIZWEB_WIZCARD_UPDATE = ('wizweb wizcard update', 1, 'your wizcard was updated')

apns_notification_dictionary = {
    WIZREQ_U[0]	: {
        'sound': 'flynn.caf',
        'badge': 0,
        #AA:TODO: separate verb from push message
        'alert': WIZREQ_U[2],
    },
    WIZREQ_T[0]	: {
        'sound': 'flynn.caf',
        'badge': 0,
        'alert': WIZREQ_T[2],
    },
    WIZCARD_ACCEPT[0]: {
        'sound': 'flynn.caf',
        'badge': 0,
        'alert': WIZCARD_ACCEPT[2],
    },
    WIZCARD_TABLE_TIMEOUT[0]: {
        'sound': 'flynn.caf',
        'badge': 0,
        'alert': WIZCARD_TABLE_TIMEOUT[2],
    },
    WIZCARD_TABLE_DESTROY[0]: {
        'sound': 'flynn.caf',
        'badge': 0,
        'alert': WIZCARD_TABLE_DESTROY[2],
    },
    WIZCARD_UPDATE[0]: {
        'sound': 'flynn.caf',
        'badge': 0,
        'alert': WIZCARD_UPDATE[2],
    },
    WIZCARD_FLICK_TIMEOUT[0]: {
        'sound': 'flynn.caf',
        'badge': 0,
        'alert': WIZCARD_FLICK_TIMEOUT[2],
    },
    WIZCARD_FLICK_PICK[0]: {
        'sound': 'flynn.caf',
        'badge': 0,
        'alert': WIZCARD_FLICK_PICK[2],
    },
    WIZWEB_WIZCARD_UPDATE[0]: {
        'sound': 'flynn.caf',
        'badge': 0,
        'alert': WIZWEB_WIZCARD_UPDATE[2],
    },
}

