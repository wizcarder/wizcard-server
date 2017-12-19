#!/usr/bin/python

# Test WizCard client (the real one resides on a smartphone - iphone, android)

# Standard imports
import httplib
import sys
import pdb
import messages
from notifications import NotifParser
import random
import string
proj_path="."
sys.path.append(proj_path)
from wizcard import settings
import libtest
from libtest import send_request, handle_response


TEST_IMAGE=True
OCR_FLAG = False
TEST_TABLE = True
TEST_FLICK = False
TEST_WIZWEB = False
OEMBED = False
SKIP_BASIC = False
TEST_ENTITY = True


USERNAME1 = messages.PHONE1+'@wizcard.com'
USERNAME2 = messages.PHONE2+'@wizcard.com'
USERNAME3 = messages.PHONE3+'@wizcard.com'
USERNAME4 = "wizweb_user1" + ''.join(random.choice(string.digits) for x in range(2))
USERNAME4_FIRST_NAME = "WizWeb_1"
USERNAME4_LAST_NAME = "Last_1"
DELETE_ROLODEX_USER1 = messages.DELETE_ROLODEX_PHONE1 + '@wizcard.com'
DELETE_ROLODEX_USER2 = messages.DELETE_ROLODEX_PHONE2 + '@wizcard.com'
DELETE_ROLODEX_USER3 = messages.DELETE_ROLODEX_PHONE3 + '@wizcard.com'

TABLE1NAME = "One"
TABLE1NAME_NEW = "One More"
TABLE2NAME = "One More More"
TABLE3NAME = "One More More More"

FIRSTNAME_Q = "a"
LASTNAME_Q = "a"

TABLENAME_Q = "one"

DEVICE_ID1 = "aaaaaaaaaaaaaaaaaaaaaaaaaa"
DEVICE_ID2 = "bbbbbbbbbbbbbbbbbbbbbbbbbb"
DEVICE_ID3 = "cccccccccccccccccccccccccc"
DEVICE_ID4 = "dddddddddddddddddddddddddd"
DEVICE_ID5 = "Reeeeeeeeeeeeeeeeeeeeeeeee"


HASH1 = "aaaaaaaaaaaaaaaaaaaaaaaaaa"
HASH2 = "bbbbbbbbbbbbbbbbbbbbbbbbbb"
HASH3 = "cccccccccccccccccccccccccc"

RESPONSE_KEY1 = "1234"
RESPONSE_KEY2 = "1234"
RESPONSE_KEY3 = "1234"

DEFAULT_TITLE = "CEO"
DEFAULT_COMPANY = "WizCard Inc"
START1 = "Jan 27, 2010"
DEFAULT_MEDIA_URL = "www.youtube.com"
DEFAULT_BIZCARD_URL = "www.youtube.com"

INDIA_INTERNATIONAL_PREFIX = '00'
INTERNATIONAL_PREFIX = '+'
INDIA_COUNTRY_CODE = '91'
USA_COUNTRY_CODE = '1'


verify_phones_list = [messages.PHONE1, messages.PHONE2, messages.PHONE3]
verify_emails_list = [messages.EMAIL1, messages.EMAIL2, messages.EMAIL3, messages.EMAIL4]

uid_list = []
wuid_list = []

server_url = "localhost"
#server_url = "ec2-54-219-163-35.us-west-1.compute.amazonaws.com"
#server_url = "ec2-54-153-11-241.us-west-1.compute.amazonaws.com"
#server_url = "ec2-52-66-102-242.ap-south-1.compute.amazonaws.com"

#server_port = 80
server_port = 8000

# Open the connection to Wiz server
conn = httplib.HTTPConnection(server_url, server_port)


if OCR_FLAG:
    f = open(libtest.ocr_image_path, 'rb')
    ocr_out = f.read().encode('base64')
else:
    ocr_out = None


if not SKIP_BASIC:
    reqmsg = messages.phone_check_req
    reqmsg['header']['device_id'] = DEVICE_ID1
    reqmsg['header']['hash'] = HASH1
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['username'] = USERNAME1
    reqmsg['sender']['target'] = messages.NEXMO_PHONE1
    reqmsg['sender']['response_mode'] = 'sms'
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    response_key = objs['data'].get('challenge_key', 1234)

    # send some more requests to simulate user retry
    reqmsg = messages.phone_check_req
    reqmsg['header']['device_id'] = DEVICE_ID1
    reqmsg['header']['hash'] = HASH1
    reqmsg['sender']['username'] = USERNAME1
    reqmsg['sender']['target'] = messages.NEXMO_PHONE1
    reqmsg['sender']['response_mode'] = 'sms'
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    reqmsg = messages.phone_check_req
    reqmsg['header']['device_id'] = DEVICE_ID1
    reqmsg['header']['hash'] = HASH1
    reqmsg['sender']['username'] = USERNAME1
    reqmsg['sender']['target'] = messages.NEXMO_PHONE1
    reqmsg['sender']['response_mode'] = 'sms'
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    reqmsg = messages.phone_check_req
    reqmsg['header']['device_id'] = DEVICE_ID1
    reqmsg['header']['hash'] = HASH1
    reqmsg['sender']['username'] = USERNAME1
    reqmsg['sender']['target'] = messages.NEXMO_PHONE1
    reqmsg['sender']['response_mode'] = 'sms'
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    # this one should be an error
    objs = handle_response(conn, reqmsg['header']['msg_type'], err_skip=True)

    reqmsg = messages.phone_check_resp
    reqmsg['header']['device_id'] = DEVICE_ID1
    reqmsg['header']['hash'] = HASH1
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['username'] = USERNAME1
    reqmsg['sender']['response_key'] = response_key
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    uid1 = objs['data']['user_id']
    uid_list.append(uid1)

    reqmsg = messages.phone_check_req
    reqmsg['header']['device_id'] = DEVICE_ID2
    reqmsg['header']['hash'] = HASH2
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['username'] = USERNAME2
    reqmsg['sender']['target'] = messages.PHONE2
    reqmsg['sender']['response_mode'] = 'sms'

    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    response_key = objs['data']['challenge_key']

    reqmsg = messages.phone_check_resp
    reqmsg['header']['device_id'] = DEVICE_ID2
    reqmsg['header']['hash'] = HASH2
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['username'] = USERNAME2
    reqmsg['sender']['response_key'] = response_key
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    uid2 = objs['data']['user_id']
    uid_list.append(uid2)

    #AnandR: Should check when the response_key doesnt match the sent response_key

    reqmsg = messages.phone_check_req
    reqmsg['header']['device_id'] = DEVICE_ID3
    reqmsg['header']['hash'] = HASH3
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['username'] = USERNAME3
    reqmsg['sender']['target'] = messages.PHONE3
    reqmsg['sender']['response_mode'] = 'sms'
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    response_key = objs['data']['challenge_key']


    #resp = objs['data']['key']
    reqmsg = messages.phone_check_resp
    reqmsg['header']['device_id'] = DEVICE_ID3
    reqmsg['header']['hash'] = HASH3
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['username'] = USERNAME3
    reqmsg['sender']['response_key'] = response_key
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    uid3 = objs['data']['user_id']
    uid_list.append(uid3)

    reqmsg = messages.login
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['username'] = USERNAME1
    reqmsg['sender']['user_id'] = uid1
    reqmsg['header']['device_id'] = DEVICE_ID1
    reqmsg['sender']['password'] = DEVICE_ID1+uid1

    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    wuid1 = objs['data']['wizuser_id']
    wuid_list.append(wuid1)

    reqmsg['sender']['username'] = USERNAME2
    reqmsg['sender']['user_id'] = uid2
    reqmsg['header']['device_id'] = DEVICE_ID2
    reqmsg['sender']['password'] = DEVICE_ID2+uid2

    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    wuid2 = objs['data']['wizuser_id']
    wuid_list.append(wuid2)

    reqmsg['sender']['username'] = USERNAME3
    reqmsg['sender']['user_id'] = uid3
    reqmsg['header']['device_id'] = DEVICE_ID3
    reqmsg['sender']['password'] = DEVICE_ID3+uid3

    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    wuid3 = objs['data']['wizuser_id']
    wuid_list.append(wuid3)

    #send register

    #create 3 users
    reqmsg = messages.register1
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id']=uid1
    reqmsg['sender']['wizuser_id']=wuid1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    reqmsg = messages.register2
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id']=uid2
    reqmsg['sender']['wizuser_id']=wuid2
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    reqmsg = messages.register3
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id']=uid3
    reqmsg['sender']['wizuser_id']=wuid3
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    reqmsg = messages.edit_card1
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    contacts = reqmsg['sender']['contact_container']
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    e1_id = objs['data']['wizcard']['wizcard_id']

    reqmsg = messages.edit_card2
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid2
    reqmsg['sender']['wizuser_id'] = wuid2
    contacts = reqmsg['sender']['contact_container']
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    e2_id = objs['data']['wizcard']['wizcard_id']

    reqmsg = messages.get_email_template
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    #send_request(conn, reqmsg)
    #objs = handle_response(conn, reqmsg['header']['msg_type'])
    #email = objs['data']['emailTemplate']
    print "Email check..."

    reqmsg = messages.edit_card3
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid3
    reqmsg['sender']['wizuser_id'] = wuid3
    contacts = reqmsg['sender']['contact_container']
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    e3_id = objs['data']['wizcard']['wizcard_id']

    #send location update
    reqmsg = messages.location
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['lat'] = messages.LAT1
    reqmsg['sender']['lng'] = messages.LNG1
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    #send get cards to seed location information
    reqmsg = messages.get_cards
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    notif = NotifParser(objs['data'], uid1, wuid1)
    nrsp = notif.process()

    reqmsg = messages.get_cards
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid2
    reqmsg['sender']['wizuser_id'] = wuid2
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    notif = NotifParser(objs['data'], uid2, wuid2)
    nrsp = notif.process()

    reqmsg = messages.get_cards
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid3
    reqmsg['sender']['wizuser_id'] = wuid3
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    notif = NotifParser(objs['data'], uid3, wuid3)
    nrsp = notif.process()

    #contacts upload user 1
    reqmsg = messages.contacts_upload
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['receiver']['prefix'] = INDIA_INTERNATIONAL_PREFIX
    reqmsg['receiver']['country_code'] = INDIA_COUNTRY_CODE
    reqmsg['receiver']['ab_list'] = messages.USER1_AB
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    #contacts upload user 2
    reqmsg = messages.contacts_upload
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid2
    reqmsg['sender']['wizuser_id'] = wuid2
    reqmsg['receiver']['prefix'] = INDIA_INTERNATIONAL_PREFIX
    reqmsg['receiver']['country_code'] = INDIA_COUNTRY_CODE
    reqmsg['receiver'].update(messages.ab_list_ananda_1)
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    #contacts upload user 3
    reqmsg = messages.contacts_upload
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid3
    reqmsg['sender']['wizuser_id'] = wuid3
    reqmsg['receiver']['prefix'] = INTERNATIONAL_PREFIX
    reqmsg['receiver'].update(messages.ab_list_baskar_1)
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    # get reco for u1
    reqmsg = messages.get_recommendations
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['sender']['size'] = 5
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    reqmsg = messages.contacts_upload
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['receiver']['prefix'] = INDIA_INTERNATIONAL_PREFIX
    reqmsg['receiver'].update(messages.ab_list_anandr_1)
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    reqmsg = messages.card_details
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['receiver']['wizcard_id'] = e1_id
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    reqmsg = messages.card_details
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid2
    reqmsg['sender']['wizuser_id'] = wuid2
    reqmsg['receiver']['wizcard_id'] = e2_id
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    reqmsg = messages.card_details
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid3
    reqmsg['sender']['wizuser_id'] = wuid3
    reqmsg['receiver']['wizcard_id'] = e3_id
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    # 1:1 Tests

    #assetToXYZ tests
    #asset types: wizcard, entity
    #receiver_type: phone, email, wizuser_id
    #u1 -> u2, u3 via wiz
    reqmsg = messages.send_asset_to_xyz
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['sender']['asset_id'] = e1_id
    reqmsg['sender']['asset_type'] = "wizcard"
    reqmsg['receiver']['receiver_type'] = "wiz_untrusted"
    reqmsg['receiver']['receiver_ids'] = [wuid2, wuid3]
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

            # connection state so far
            # uid1(A)<->uid2(P)
            # uid1(A)<->uid3(P)

    #u1 -> future_u1, u2 via sms
    reqmsg = messages.send_asset_to_xyz
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['sender']['asset_id'] = e1_id
    reqmsg['sender']['asset_type'] = "wizcard"
    reqmsg['receiver']['receiver_type'] = "sms"
    reqmsg['receiver']['receiver_ids'] = [messages.FUTURE_PHONE1, messages.FUTURE_PHONE2]
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    #u2 -> future u1, u2 via email
    reqmsg['sender']['user_id'] = uid2
    reqmsg['sender']['asset_type'] = "wizcard"
    reqmsg['sender']['wizuser_id'] = wuid2
    reqmsg['sender']['asset_id'] = e2_id
    reqmsg['receiver']['receiver_type'] = "email"
    reqmsg['receiver']['receiver_ids'] = [messages.FUTURE_EMAIL1, messages.FUTURE_EMAIL2]
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])


    # Self invite - Should throw an error
    reqmsg = messages.send_asset_to_xyz
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['sender']['asset_id'] = e1_id
    reqmsg['sender']['asset_type'] = "wizcard"
    reqmsg['receiver']['receiver_type'] = "sms"
    reqmsg['receiver']['receiver_ids'] = [messages.SELF_PHONE]
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'], err_skip=True)

    # Self invite + some other number - Shouldnt  throw an error and silently pass
    reqmsg = messages.send_asset_to_xyz
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['sender']['asset_id'] = e1_id
    reqmsg['sender']['asset_type'] = "wizcard"
    reqmsg['receiver']['receiver_type'] = "sms"
    reqmsg['receiver']['receiver_ids'] = [messages.SELF_PHONE,messages.FUTURE_PHONE1]
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    #now create future u1 and u2

    print "creating future user 1 and 2"
    reqmsg = messages.phone_check_req
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['header']['device_id'] = DEVICE_ID4
    reqmsg['header']['hash'] = HASH2
    reqmsg['sender']['username'] = messages.FUTURE_USERNAME1
    reqmsg['sender']['target'] = messages.FUTURE_PHONE1
    reqmsg['sender']['response_mode'] = 'sms'

    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    response_key = objs['data']['challenge_key']

    reqmsg = messages.phone_check_resp
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['header']['device_id'] = DEVICE_ID4
    reqmsg['header']['hash'] = HASH2
    reqmsg['sender']['username'] = messages.FUTURE_USERNAME1
    reqmsg['sender']['response_key'] = response_key
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    fuid1 = objs['data']['user_id']

    reqmsg = messages.phone_check_req
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['header']['device_id'] = DEVICE_ID5
    reqmsg['header']['hash'] = HASH2
    reqmsg['sender']['username'] = messages.FUTURE_USERNAME2
    reqmsg['sender']['target'] = messages.FUTURE_PHONE2
    reqmsg['sender']['response_mode'] = 'sms'

    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    response_key = objs['data']['challenge_key']

    reqmsg = messages.phone_check_resp
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['header']['device_id'] = DEVICE_ID5
    reqmsg['header']['hash'] = HASH2
    reqmsg['sender']['username'] = messages.FUTURE_USERNAME2
    reqmsg['sender']['response_key'] = response_key
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    fuid2 = objs['data']['user_id']

    print "logging in future user 1 and 2"
    reqmsg = messages.login
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['username'] = messages.FUTURE_USERNAME1
    reqmsg['sender']['user_id'] = fuid1
    reqmsg['header']['device_id'] = DEVICE_ID4
    reqmsg['sender']['password'] = DEVICE_ID4+fuid1

    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    fwuid1 = objs['data']['wizuser_id']

    reqmsg['sender']['username'] = messages.FUTURE_USERNAME2
    reqmsg['sender']['user_id'] = fuid2
    reqmsg['header']['device_id'] = DEVICE_ID5
    reqmsg['sender']['password'] = DEVICE_ID5+fuid2

    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    fwuid2 = objs['data']['wizuser_id']

    print "registering future user 1 and 2"
    reqmsg = messages.register1
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id']=fuid1
    reqmsg['sender']['wizuser_id']=fwuid1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    reqmsg = messages.register2
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id']=fuid2
    reqmsg['sender']['wizuser_id']=fwuid2
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    print "creating wizcard for future user"
    reqmsg = messages.edit_card1
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = fuid1
    reqmsg['sender']['wizuser_id'] = fwuid1
    reqmsg['sender']['email'] = messages.FUTURE_EMAIL1
    reqmsg['sender']['phone1'] = messages.FUTURE_PHONE1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    fe1_id = objs['data']['wizcard']['wizcard_id']

    reqmsg = messages.edit_card1
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = fuid2
    reqmsg['sender']['wizuser_id'] = fwuid2
    reqmsg['sender']['email'] = messages.FUTURE_EMAIL2
    reqmsg['sender']['phone1'] = messages.FUTURE_PHONE2
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    fe2_id = objs['data']['wizcard']['wizcard_id']

            # connection state so far
            # uid1(A)<->uid2(P)
            # uid1(A)<->uid3(P)
            # uid1(A)<->fuid1(P)
            # uid1(A)<->fuid2(P)

    #at this point there should be notifs for this user
    reqmsg = messages.get_cards
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    notif = NotifParser(objs['data'], uid1, wuid1)
    nrsp = notif.process()

    reqmsg = messages.get_cards
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid2
    reqmsg['sender']['wizuser_id'] = wuid2
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    notif = NotifParser(objs['data'], uid2, wuid2)
    nrsp = notif.process()

    reqmsg = messages.get_cards
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid3
    reqmsg['sender']['wizuser_id'] = wuid3
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    notif = NotifParser(objs['data'], uid3, wuid3)
    nrsp = notif.process()

    reqmsg = messages.get_cards
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = fuid1
    reqmsg['sender']['wizuser_id'] = fwuid1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    notif = NotifParser(objs['data'], fuid1, fwuid1)
    nrsp = notif.process()

    reqmsg = messages.get_cards
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = fuid2
    reqmsg['sender']['wizuser_id'] = fwuid2
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    notif = NotifParser(objs['data'], fuid2, fwuid2)
    nrsp = notif.process()

            # connection state so far
            # uid1(A)<->uid2(P)
            # uid1(A)<->uid3(P)
            # uid1(A)<->fuid1(P)
            # uid1(A)<->fuid2(P)

    # uid2 accept uid1
    reqmsg = messages.accept_connection_request
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid2
    reqmsg['sender']['wizuser_id'] = wuid2
    reqmsg['receiver']['wizuser_id'] = wuid1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

            # uid1(A)<->uid2(A)
            # uid1(A)<->uid3(P)
            # uid1(A)<->fuid1(P)
            # uid1(A)<->fuid2(P)

    # uid3 decline uid1
    reqmsg = messages.decline_connection_request
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid3
    reqmsg['sender']['wizuser_id'] = wuid3
    reqmsg['receiver']['wizcard_id'] = e1_id
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

            # uid1(A)<->uid2(A)
            # uid1(A)<->uid3(DC)
            # uid1(A)<->fuid1(P)
            # uid1(A)<->fuid2(P)

    # fuid1 accept
    reqmsg = messages.accept_connection_request
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = fuid1
    reqmsg['sender']['wizuser_id'] = fwuid1
    reqmsg['receiver']['wizuser_id'] = wuid1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

            # uid1(A)<->uid2(A)
            # uid1(A)<->uid3(DC)
            # uid1(A)<->fuid1(A)
            # uid1(A)<->fuid2(P)

    # fuid2 decline
    reqmsg = messages.decline_connection_request
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = fuid2
    reqmsg['sender']['wizuser_id'] = fwuid2
    reqmsg['receiver']['wizcard_id'] = e1_id
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

            # uid1(A)<->uid2(A)
            # uid1(A)<->uid3(DC)
            # uid1(A)<->fuid1(A)
            # uid1(A)<->fuid2(DC)

    #u1 delete U2 rolodex
    reqmsg = messages.delete_rolodex_card
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['receiver']['wizcard_ids'] = map(lambda x: {"wizcard_id": x, "dead_card":False}, [e2_id])
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

            # uid1(DL)<->uid2(A)
            # uid1(A)<->uid3(D)
            # uid1(A)<->fuid1(P)
            # uid1(A)<->fuid2(D)

    #u1 reaccept U2
    reqmsg = messages.accept_connection_request
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['sender']['flag'] = "reaccept"
    reqmsg['receiver']['wizuser_id'] = wuid2
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

            # uid1(A)<->uid2(A)
            # uid1(A)<->uid3(DC)
            # uid1(A)<->fuid1(A)
            # uid1(A)<->fuid2(DC)

    #u3 reaccept u1
    reqmsg = messages.accept_connection_request
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid3
    reqmsg['sender']['wizuser_id'] = wuid3
    reqmsg['sender']['flag'] = "reaccept"
    reqmsg['receiver']['wizuser_id'] = wuid1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

            # uid1(A)<->uid2(A)
            # uid1(A)<->uid3(A)
            # uid1(A)<->fuid1(A)
            # uid1(A)<->fuid2(DC)


    # Do it again (bug test)
    reqmsg = messages.accept_connection_request
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid3
    reqmsg['sender']['wizuser_id'] = wuid3
    reqmsg['sender']['flag'] = "reaccept"
    reqmsg['receiver']['wizuser_id'] = wuid1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])


    # get common connections between 2 and 3
    reqmsg = messages.get_common_connections
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid2
    reqmsg['sender']['wizuser_id'] = wuid2
    reqmsg['sender']['wizcard_id'] = e2_id
    reqmsg['sender']['more'] = False
    reqmsg['receiver']['wizcard_id'] = e3_id
    send_request(conn, reqmsg)
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    # u1 delete U2 Rolodex
    reqmsg = messages.delete_rolodex_card
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['receiver']['wizcard_ids'] = map(lambda x: {"wizcard_id": x, "dead_card":False}, [e2_id])
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

            # uid1(DL)<->uid2(A)
            # uid1(A)<->uid3(A)
            # uid1(A)<->fuid1(A)
            # uid1(A)<->fuid2(DC)

    #u1 unarchive u2
    reqmsg = messages.accept_connection_request
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['sender']['flag'] = "unarchive"
    reqmsg['receiver']['wizuser_id'] = wuid2
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

            # uid1(A)<->uid2(A)
            # uid1(A)<->uid3(A)
            # uid1(A)<->fuid1(A)
            # uid1(A)<->fuid2(DC)

    # u1 delete U2 Rolodex
    reqmsg = messages.delete_rolodex_card
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['receiver']['wizcard_ids'] = map(lambda x: {"wizcard_id": x, "dead_card":False}, [e2_id])
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

            # uid1(DL)<->uid2(A)
            # uid1(A)<->uid3(A)
            # uid1(A)<->fuid1(A)
            # uid1(A)<->fuid2(DC)

    # u1 <-> U2
    reqmsg = messages.send_asset_to_xyz
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['sender']['asset_id'] = e1_id
    reqmsg['sender']['asset_type'] = "wizcard"
    reqmsg['receiver']['receiver_type'] = "wiz_untrusted"
    reqmsg['receiver']['receiver_ids'] = [wuid2]
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

            # uid1(A)<->uid2(A)
            # uid1(A)<->uid3(A)
            # uid1(A)<->fuid1(A)
            # uid1(A)<->fuid2(DC)

    #U2 delete U1 rolodex
    reqmsg = messages.delete_rolodex_card
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid2
    reqmsg['sender']['wizuser_id'] = wuid2
    reqmsg['receiver']['wizcard_ids'] = map(lambda x: {"wizcard_id": x, "dead_card":False}, [e1_id])
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

            # uid1(A)<->uid2(DL)
            # uid1(A)<->uid3(A)
            # uid1(A)<->fuid1(A)
            # uid1(A)<->fuid2(DC)

    # u1 invite fuid1 when connected
    reqmsg = messages.send_asset_to_xyz
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['sender']['asset_id'] = e1_id
    reqmsg['sender']['asset_type'] = "wizcard"
    reqmsg['receiver']['receiver_type'] = "sms"
    reqmsg['receiver']['receiver_ids'] = [messages.FUTURE_PHONE1]
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

            # uid1(A)<->uid2(DL)
            # uid1(A)<->uid3(A)
            # uid1(A)<->fuid1(A)
            # uid1(A)<->fuid2(DC)

    # u1 delete card fuid2
    reqmsg = messages.delete_rolodex_card
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['receiver']['wizcard_ids'] = map(lambda x: {"wizcard_id": x, "dead_card":False}, [fe2_id])
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

            # uid1(A)<->uid2(DL)
            # uid1(A)<->uid3(A)
            # uid1(A)<->fuid1(A)
            # uid1(DL)<->fuid2(DC)

    # AA: Debug this
    # u1 invite fuid2 when declined
    reqmsg = messages.send_asset_to_xyz
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['sender']['asset_id'] = e1_id
    reqmsg['sender']['asset_type'] = "wizcard"
    reqmsg['receiver']['receiver_type'] = "sms"
    reqmsg['receiver']['receiver_ids'] = [messages.FUTURE_PHONE2]
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

            # uid1(A)<->uid2(DL)
            # uid1(A)<->uid3(A)
            # uid1(A)<->fuid1(A)
            # uid1(A)<->fuid2(P)

    # fuid2 accept u1
    reqmsg = messages.accept_connection_request
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = fuid2
    reqmsg['sender']['wizuser_id'] = fwuid2
    reqmsg['receiver']['wizuser_id'] = wuid1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

            # uid1(A)<->uid2(DL)
            # uid1(A)<->uid3(A)
            # uid1(A)<->fuid1(A)
            # uid1(A)<->fuid2(A)

    #delete all rolodex card of u1
    print "deleting all cards of ", uid1
    reqmsg = messages.delete_rolodex_card
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['receiver']['wizcard_ids'] = map(lambda x: {"wizcard_id": x, "dead_card":False}, [e2_id, e3_id, fe1_id, fe2_id])
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

            # uid1(DL)<->uid2(DL)
            # uid1(DL)<->uid3(A)
            # uid1(DL)->fuid1(A)
            # uid1(DL) fuid2(A)

    # u1 edit rolodex card of u3
    print "adding notes to  ", uid3
    reqmsg = messages.edit_rolodex_card
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['receiver']['wizcard_id'] = e3_id
    reqmsg['receiver']['notes']['note'] = "test one test two"
    reqmsg['receiver']['notes']['last_saved'] = "1st Jan 2016"

    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    #user query
    reqmsg = messages.user_query
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid3
    reqmsg['sender']['wizuser_id'] = wuid3
    reqmsg['receiver']['name'] = FIRSTNAME_Q
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    # archived cards
    reqmsg = messages.archived_cards
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    # Meishi
    reqmsg = messages.meishi_start
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid2
    reqmsg['sender']['wizuser_id'] = wuid2
    reqmsg['sender']['wizcard_id'] = e1_id
    reqmsg['sender']['lat'] = messages.LAT1
    reqmsg['sender']['lng'] = messages.LNG1
    send_request(conn, reqmsg)
    objs = handle_response(conn,reqmsg['header']['msg_type'])
    mei_id2 = objs['data']['mID']
    m_nearby = objs['data']['m_nearby']

    reqmsg = messages.meishi_find
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid2
    reqmsg['sender']['wizuser_id'] = wuid2
    reqmsg['sender']['mID'] = mei_id2
    send_request(conn, reqmsg)
    objs = handle_response(conn,reqmsg['header']['msg_type'])
    if objs['data'].has_key('m_result'):
        mei_pair = objs['data']['m_result']
    else:
        # expect nearby response
        m_nearby = objs['data']['m_nearby']

    #DELETE_ROLODEX_CASE

    reqmsg = messages.phone_check_req
    reqmsg['header']['device_id'] = DEVICE_ID1
    reqmsg['header']['hash'] = HASH1
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['username'] = DELETE_ROLODEX_USER1
    reqmsg['sender']['target'] = messages.NEXMO_PHONE1
    reqmsg['sender']['response_mode'] = 'sms'
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    response_key = objs['data'].get('challenge_key', 1234)

    reqmsg = messages.phone_check_resp
    reqmsg['header']['device_id'] = DEVICE_ID1
    reqmsg['header']['hash'] = HASH1
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['username'] = DELETE_ROLODEX_USER1
    reqmsg['sender']['response_key'] = response_key
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    duid1 = objs['data']['user_id']

    reqmsg = messages.login
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['username'] = DELETE_ROLODEX_USER1
    reqmsg['sender']['user_id'] = duid1
    reqmsg['header']['device_id'] = DEVICE_ID1
    reqmsg['sender']['password'] = DEVICE_ID1+duid1

    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    dwuid1 = objs['data']['wizuser_id']

    reqmsg = messages.phone_check_req
    reqmsg['header']['device_id'] = DEVICE_ID2
    reqmsg['header']['hash'] = HASH1
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['username'] = DELETE_ROLODEX_USER2
    reqmsg['sender']['target'] = messages.NEXMO_PHONE1
    reqmsg['sender']['response_mode'] = 'sms'
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    response_key = objs['data'].get('challenge_key', 1234)

    reqmsg = messages.phone_check_resp
    reqmsg['header']['device_id'] = DEVICE_ID2
    reqmsg['header']['hash'] = HASH1
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['username'] = DELETE_ROLODEX_USER2
    reqmsg['sender']['response_key'] = response_key
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    duid2 = objs['data']['user_id']

    reqmsg = messages.login
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['username'] = DELETE_ROLODEX_USER2
    reqmsg['sender']['user_id'] = duid2
    reqmsg['header']['device_id'] = DEVICE_ID2
    reqmsg['sender']['password'] = DEVICE_ID2+duid2

    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    dwuid2 = objs['data']['wizuser_id']

    reqmsg = messages.phone_check_req
    reqmsg['header']['device_id'] = DEVICE_ID3
    reqmsg['header']['hash'] = HASH1
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['username'] = DELETE_ROLODEX_USER3
    reqmsg['sender']['target'] = messages.NEXMO_PHONE1
    reqmsg['sender']['response_mode'] = 'sms'
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    response_key = objs['data'].get('challenge_key', 1234)

    reqmsg = messages.phone_check_resp
    reqmsg['header']['device_id'] = DEVICE_ID3
    reqmsg['header']['hash'] = HASH1
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['username'] = DELETE_ROLODEX_USER3
    reqmsg['sender']['response_key'] = response_key
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    duid3 = objs['data']['user_id']

    reqmsg = messages.login
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['username'] = DELETE_ROLODEX_USER3
    reqmsg['sender']['user_id'] = duid3
    reqmsg['header']['device_id'] = DEVICE_ID3
    reqmsg['sender']['password'] = DEVICE_ID3+duid3

    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    dwuid3 = objs['data']['wizuser_id']

    reqmsg = messages.register1
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = duid1
    reqmsg['sender']['wizuser_id'] = dwuid1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    reqmsg = messages.register2
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = duid2
    reqmsg['sender']['wizuser_id'] = dwuid2
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    reqmsg = messages.register3
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = duid3
    reqmsg['sender']['wizuser_id'] = dwuid3
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    reqmsg = messages.rolodex_edit_card1
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = duid1
    reqmsg['sender']['wizuser_id'] = dwuid1
    contacts = reqmsg['sender']['contact_container']

    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    e1_id = objs['data']['wizcard']['wizcard_id']

    reqmsg = messages.rolodex_edit_card2
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = duid2
    reqmsg['sender']['wizuser_id'] = dwuid2
    contacts = reqmsg['sender']['contact_container']

    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    e2_id = objs['data']['wizcard']['wizcard_id']

    reqmsg = messages.rolodex_edit_card3
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = duid3
    reqmsg['sender']['wizuser_id'] = dwuid3
    contacts = reqmsg['sender']['contact_container']

    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    e3_id = objs['data']['wizcard']['wizcard_id']

    reqmsg = messages.send_asset_to_xyz
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = duid1
    reqmsg['sender']['wizuser_id'] = dwuid1
    reqmsg['sender']['asset_id'] = e1_id
    reqmsg['sender']['asset_type'] = "wizcard"
    reqmsg['receiver']['receiver_type'] = "wiz_untrusted"
    reqmsg['receiver']['receiver_ids'] = [dwuid2, dwuid3]
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    # send get cards to clear readed on one guy
    reqmsg = messages.get_cards
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = duid2
    reqmsg['sender']['wizuser_id'] = dwuid2
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    # delete. Expect 3 to go back to new state, and 2 will follow error 24 path upon
    # accept/decline
    reqmsg = messages.delete_rolodex_card
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = duid1
    reqmsg['sender']['wizuser_id'] = dwuid1
    reqmsg['receiver']['wizcard_ids'] = map(lambda x: {"wizcard_id": x, "dead_card":False}, [e2_id, e3_id])
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    # uid2 accept uid1
    reqmsg = messages.accept_connection_request
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = duid2
    reqmsg['sender']['wizuser_id'] = dwuid2
    reqmsg['receiver']['wizuser_id'] = dwuid1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    # recreate 1<->3 to test decline path
    reqmsg = messages.send_asset_to_xyz
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = duid1
    reqmsg['sender']['wizuser_id'] = dwuid1
    reqmsg['sender']['asset_id'] = e1_id
    reqmsg['sender']['asset_type'] = "wizcard"
    reqmsg['receiver']['receiver_type'] = "wiz_untrusted"
    reqmsg['receiver']['receiver_ids'] = [dwuid3]
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    # send get cards to clear readed on 3
    reqmsg = messages.get_cards
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = duid3
    reqmsg['sender']['wizuser_id'] = dwuid3
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    reqmsg = messages.delete_rolodex_card
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = duid1
    reqmsg['sender']['wizuser_id'] = dwuid1
    reqmsg['receiver']['wizcard_ids'] = map(lambda x: {"wizcard_id": x, "dead_card":False}, [e3_id])
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    #uid3 declines uid1
    reqmsg = messages.decline_connection_request
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = duid3
    reqmsg['sender']['wizuser_id'] = dwuid3
    reqmsg['receiver']['wizcard_id'] = e1_id
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

if OEMBED:
    reqmsg = messages.get_video_thumbnail_url
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['sender']['video_url'] = "https://s3-us-west-1.amazonaws.com/wizcard-image-bucket-dev/bizcards/test_video.mp4"
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    # this one will work with oembed
    reqmsg = messages.get_video_thumbnail_url
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['sender']['video_url'] = "https://www.youtube.com/watch?v=QujpdmsXAb4&feature=youtu.be"
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    # this one will return error
    reqmsg = messages.get_video_thumbnail_url
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['sender']['video_url'] = "https://noembed.com/embed?url=https://youtu.be/kvjxoBG5euo"
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'], err_skip=True)
#clean all rolodexes


# Table Tests
if TEST_TABLE:
    reqmsg = messages.entity_create
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['sender']['name'] = TABLE1NAME
    reqmsg['sender']['timeout'] = 1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    tid_1 = objs['data']['result']['id']

    reqmsg = messages.entity_create
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid2
    reqmsg['sender']['wizuser_id'] = wuid2
    reqmsg['sender']['name'] = TABLE2NAME
    reqmsg['sender']['timeout'] = 5
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    tid_2 = objs['data']['result']['id']

    #join created entity
    print "Joining Table"

    reqmsg = messages.entity_join
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid2
    reqmsg['sender']['wizuser_id'] = wuid2
    reqmsg['sender']['entity_id'] = tid_1
    reqmsg['sender']['entity_type'] = 'TBL'

    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    print "Joining Table with error password"
    reqmsg = messages.entity_join
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid3
    reqmsg['sender']['wizuser_id'] = wuid3
    reqmsg['sender']['entity_id'] = tid_1
    reqmsg['sender']['entity_type'] = 'TBL'
    reqmsg['sender']['password'] = "xxx"
    # Parse and dump the JSON response from server
    send_request(conn, reqmsg)
    objs = handle_response(conn, reqmsg['header']['msg_type'], err_skip=True)

    print "Edit Table"
    reqmsg = messages.entity_edit
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['sender']['entity_id'] = tid_1
    reqmsg['sender']['entity_type'] = 'TBL'
    reqmsg['sender']['name'] = TABLE1NAME_NEW
    reqmsg['sender']['timeout'] = 5
    # Parse and dump the JSON response from server
    send_request(conn, reqmsg)
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    print "Creating Table Three"
    reqmsg = messages.entity_create
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid3
    reqmsg['sender']['wizuser_id'] = wuid3
    reqmsg['sender']['name'] = TABLE3NAME
    reqmsg['sender']['entity_type'] = 'TBL'
    reqmsg['sender']['timeout'] = 5
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    tid_3 = objs['data']['result']['id']

    # entity query
    print "sending entity query"
    reqmsg = messages.entity_query
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid3
    reqmsg['sender']['wizuser_id'] = wuid3
    reqmsg['sender']['query_str'] = TABLENAME_Q
    reqmsg['sender']['entity_type'] = 'TBL'

    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    # entity summary
    print "sending entity summary"
    reqmsg = messages.entity_summary
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid2
    reqmsg['sender']['wizuser_id'] = wuid2
    reqmsg['sender']['entity_id'] = tid_1
    reqmsg['sender']['entity_type'] = 'TBL'

    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    #table details
    print "sending table details"
    reqmsg = messages.entity_summary
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid2
    reqmsg['sender']['wizuser_id'] = wuid2
    reqmsg['sender']['entity_id'] = tid_1
    reqmsg['sender']['detail'] = True
    reqmsg['sender']['entity_type'] = 'TBL'

    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    print "my entities"
    reqmsg = messages.my_entities
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['sender']['entity_id'] = tid_1
    reqmsg['sender']['entity_type'] = None

    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    #t1 -> fu3, fu4 via email, asset_type = Table
    reqmsg = messages.send_asset_to_xyz
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['sender']['asset_id'] = tid_1
    reqmsg['sender']['asset_type'] = "table"
    reqmsg['receiver']['receiver_type'] = "email"
    reqmsg['receiver']['receiver_ids'] = [messages.FUTURE_EMAIL3, messages.FUTURE_EMAIL4]
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    #t2 -> fu3, fu4 via sms, asset_type = Table
    reqmsg = messages.send_asset_to_xyz
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid2
    reqmsg['sender']['wizuser_id'] = wuid2
    reqmsg['sender']['asset_id'] = tid_2
    reqmsg['sender']['asset_type'] = "table"
    reqmsg['receiver']['receiver_type'] = "sms"
    reqmsg['receiver']['receiver_ids'] = [messages.FUTURE_PHONE3, messages.FUTURE_PHONE4]
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])


# Flick Tests
if TEST_FLICK:
    reqmsg = messages.card_flick
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    cf1_id = objs['data']['flickCardID']

    #re flick to check agglomeration
    reqmsg = messages.card_flick
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid2
    reqmsg['sender']['wizuser_id'] = wuid2
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    cf2_id = objs['data']['flickCardID']

    #re flick to check agglomeration with delta lat,lng
    reqmsg = messages.card_flick
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    print "re-flicking card from close-by location", reqmsg['sender']['user_id']
    reqmsg['sender']['lng'] += 0.000001
    reqmsg['sender']['lat'] += 0.000001
    reqmsg['sender']['timeout'] = 2
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    cf3_id = objs['data']['flickCardID']
    if cf3_id != cf1_id:
        print "ERROR in DELTA AGGLORMERATION"


    #edit flick
    reqmsg = messages.card_flick_edit
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['sender']['flickCardID'] = cf1_id
    reqmsg['sender']['timeout'] = 1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    reqmsg = messages.card_flick
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid3
    reqmsg['sender']['wizuser_id'] = wuid3
    reqmsg['sender']['timeout'] = 3
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    cf3_id = objs['data']['flickCardID']

    reqmsg = messages.card_flick_accept
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['receiver']['flickCardIDs'] = [cf3_id]
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    reqmsg = messages.flick_pickers
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid3
    reqmsg['sender']['wizuser_id'] = wuid3
    reqmsg['sender']['flickCardID'] = cf3_id
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    reqmsg = messages.my_flicks
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['sender']['wizcard_id'] = e1_id
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    reqmsg = messages.my_flicks
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid3
    reqmsg['sender']['wizuser_id'] = wuid3
    reqmsg['sender']['wizcard_id'] = e3_id
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])

    #flick query
    reqmsg = messages.card_flick_query
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid3
    reqmsg['sender']['wizuser_id'] = wuid3
    reqmsg['receiver']['name'] = FIRSTNAME_Q
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])


if OCR_FLAG:
    #OCR USER
    reqmsg = messages.phone_check_req
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['header']['device_id'] = DEVICE_ID3
    reqmsg['header']['hash'] = HASH3
    reqmsg['sender']['username'] = messages.OCR_USERNAME
    reqmsg['sender']['target'] = messages.OCR_PHONE
    reqmsg['sender']['response_mode'] = 'sms'
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    response_key = objs['data']['challenge_key']

    #resp = objs['data']['key']
    reqmsg = messages.phone_check_resp
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['header']['device_id'] = DEVICE_ID3
    reqmsg['header']['hash'] = HASH3
    reqmsg['sender']['username'] = messages.OCR_USERNAME
    reqmsg['sender']['response_key'] = response_key
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    ocr_uid = objs['data']['user_id']

    reqmsg = messages.login
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['username'] = messages.OCR_USERNAME
    reqmsg['sender']['user_id'] = ocr_uid
    reqmsg['header']['device_id'] = DEVICE_ID3
    reqmsg['sender']['password'] = DEVICE_ID3+ocr_uid

    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    ocr_wuid = objs['data']['wizuser_id']

    reqmsg = messages.ocr_req_self
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = ocr_uid
    reqmsg['sender']['wizuser_id'] = ocr_wuid
    reqmsg['sender']['f_ocr_card_image'] = ocr_out
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'], err_skip=True)
    if not objs['result']['Error']:
        contact_container = objs['data']['ocr_result']['contact_container']

    reqmsg = messages.ocr_dead_card
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['sender']['f_ocr_card_image'] = ocr_out
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'], err_skip=True)
    if not objs['result']['Error']:
        dc1_id = objs['data']['response']['wizcard_id']

        reqmsg = messages.ocr_dead_card_edit
        reqmsg['header']['version'] = messages.APP_VERSION
        reqmsg['sender']['user_id'] = uid1
        reqmsg['sender']['wizuser_id'] = wuid1
        reqmsg['sender']['wizcard_id'] = dc1_id
        reqmsg['sender']['inviteother'] = 0
        reqmsg['sender']['contact_container'][0]['email'] = 'anandramani98@gmail.com'
        reqmsg['sender']['notes']['note'] = "Test Dead Card notes"
        reqmsg['sender']['notes']['last_saved'] = "1st Jan 2016"
        send_request(conn, reqmsg)
        # Parse and dump the JSON response from server
        objs = handle_response(conn, reqmsg['header']['msg_type'])

    reqmsg = messages.delete_rolodex_card
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1
    reqmsg['receiver']['wizcard_ids'] = map(lambda x: {"wizcard_id": x, "dead_card": True}, [dc1_id])
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])


if TEST_ENTITY:
    reqmsg = messages.get_events
    reqmsg['header']['version'] = messages.APP_VERSION
    reqmsg['sender']['lat'] = messages.LAT1
    reqmsg['sender']['lng'] = messages.LNG1
    reqmsg['sender']['user_id'] = uid1
    reqmsg['sender']['wizuser_id'] = wuid1

    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msg_type'])
    event_list = []
    if 'result' in objs['data']:
        event_list = [(x['id'], x['entity_type']) for x in objs['data']['result']]

    if event_list:
        for e_id, e_type in event_list:
            reqmsg = messages.entity_join
            reqmsg['header']['version'] = messages.APP_VERSION
            reqmsg['sender']['user_id'] = uid1
            reqmsg['sender']['wizuser_id'] = wuid1
            reqmsg['sender']['entity_id'] = e_id
            reqmsg['sender']['entity_type'] = e_type

            send_request(conn, reqmsg)
            # Parse and dump the JSON response from server
            objs = handle_response(conn, reqmsg['header']['msg_type'])

            reqmsg = messages.entities_like
            reqmsg['header']['version'] = messages.APP_VERSION
            reqmsg['sender']['user_id'] = uid1
            reqmsg['sender']['wizuser_id'] = wuid1

            likes = []
            for index, item in enumerate(event_list):
                d = messages.ENTITY_LIKE.copy()
                d['entity_id'] = item[0]
                d['entity_type'] = item[1]
                d['like_level'] = random.choice(messages.LIKE_LEVELS)
                likes.append(d)
            reqmsg['sender']['likes'] = likes

            send_request(conn, reqmsg)
            # Parse and dump the JSON response from server
            objs = handle_response(conn, reqmsg['header']['msg_type'])

            reqmsg = messages.entity_details
            reqmsg['header']['version'] = messages.APP_VERSION
            reqmsg['sender']['user_id'] = uid1
            reqmsg['sender']['wizuser_id'] = wuid1
            reqmsg['sender']['entity_id'] = e_id
            reqmsg['sender']['entity_type'] = e_type
            reqmsg['sender']['detail'] = True

            send_request(conn, reqmsg)
            # Parse and dump the JSON response from server
            objs = handle_response(conn, reqmsg['header']['msg_type'])

            # polls. Check if any of the objs has a poll
            poll = libtest.check_obj_for_key(objs, 'polls')
            if poll:
                from api_test import Poll
                for p in poll:
                    rand = random.choice(range(0, len(uid_list)))
                    inst = Poll(uid_list[rand], wuid_list[rand], **p)
                    inst.prepare_response()
                    inst.send()

            reqmsg = messages.entity_leave
            reqmsg['header']['version'] = messages.APP_VERSION
            reqmsg['sender']['user_id'] = uid1
            reqmsg['sender']['wizuser_id'] = wuid1
            reqmsg['sender']['entity_id'] = e_id
            reqmsg['sender']['entity_type'] = e_type

            send_request(conn, reqmsg)
            # Parse and dump the JSON response from server
            objs = handle_response(conn, reqmsg['header']['msg_type'])


