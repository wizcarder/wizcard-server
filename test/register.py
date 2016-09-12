#!/usr/bin/python

# Test WizCard client (the real one resides on a smartphone - iphone, android)

# Standard imports
import httplib
import sys
import json
import pdb
import messages
from notifications import NotifParser
import random
import string
import pprint
proj_path="."
sys.path.append(proj_path)
from wizcard import settings


TEST_IMAGE=False
OCR_FLAG = False
TEST_TABLE = False
TEST_FLICK = False
TEST_WIZWEB = False
APP_VERSION = str(settings.APP_MAJOR) + "." +  str(settings.APP_MINOR)

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
INDIA_COUNTRY_CODE = '91'


verify_phones_list = [messages.PHONE1, messages.PHONE2, messages.PHONE3]
verify_emails_list = [messages.EMAIL1, messages.EMAIL2, messages.EMAIL3, messages.EMAIL4]

server_url = "localhost"
#server_url = "ec2-54-219-163-35.us-west-1.compute.amazonaws.com"
#server_url = "ec2-54-153-11-241.us-west-1.compute.amazonaws.com"
#server_url = "ec2-52-66-102-242.ap-south-1.compute.amazonaws.com"

#server_port = 80
server_port = 8000

test_image_path = "test/photo.JPG"
ocr_image_path = "test/1-f_bc.2.2015-06-21_2056.jpg"
# Open the connection to Wiz server
conn = httplib.HTTPConnection(server_url, server_port)

#send edit_cards for each
if TEST_IMAGE:
    f = open(test_image_path, 'rb')
    cc_out = f.read().encode('base64')
else:
    cc_out = None

if OCR_FLAG:
    f = open(ocr_image_path, 'rb')
    ocr_out = f.read().encode('base64')
else:
    ocr_out = None


def send_request(conn, req):
    print("Sending ", req['header']['msgType'])
    pprint.pprint(req)
    jreq = json.dumps(req)
    conn.request("POST", "", jreq)

def handle_response(conn, msg_type):
    res = conn.getresponse()
    print res.status, res.reason
    objs = res.read()
    objs = json.loads( objs )
    print "received respone for Message: ", msg_type
    print json.dumps(objs, sort_keys = True, indent = 2)
    return objs

reqmsg = messages.phone_check_req
reqmsg['header']['deviceID'] = DEVICE_ID1
reqmsg['header']['hash'] = HASH1
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['username'] = USERNAME1
reqmsg['sender']['target'] = messages.NEXMO_PHONE1
reqmsg['sender']['responseMode'] = 'sms'
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
response_key = objs['data'].get('challenge_key', 1234)

# send some more requests to simulate user retry
reqmsg = messages.phone_check_req
reqmsg['header']['deviceID'] = DEVICE_ID1
reqmsg['header']['hash'] = HASH1
reqmsg['sender']['username'] = USERNAME1
reqmsg['sender']['target'] = messages.NEXMO_PHONE1
reqmsg['sender']['responseMode'] = 'sms'
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.phone_check_req
reqmsg['header']['deviceID'] = DEVICE_ID1
reqmsg['header']['hash'] = HASH1
reqmsg['sender']['username'] = USERNAME1
reqmsg['sender']['target'] = messages.NEXMO_PHONE1
reqmsg['sender']['responseMode'] = 'sms'
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.phone_check_req
reqmsg['header']['deviceID'] = DEVICE_ID1
reqmsg['header']['hash'] = HASH1
reqmsg['sender']['username'] = USERNAME1
reqmsg['sender']['target'] = messages.NEXMO_PHONE1
reqmsg['sender']['responseMode'] = 'sms'
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
# this one should be an error
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.phone_check_resp
reqmsg['header']['deviceID'] = DEVICE_ID1
reqmsg['header']['hash'] = HASH1
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['username'] = USERNAME1
reqmsg['sender']['responseKey'] = response_key
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
uid1 = objs['data']['userID']

reqmsg = messages.phone_check_req
reqmsg['header']['deviceID'] = DEVICE_ID2
reqmsg['header']['hash'] = HASH2
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['username'] = USERNAME2
reqmsg['sender']['target'] = messages.PHONE2
reqmsg['sender']['responseMode'] = 'sms'

send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
response_key = objs['data']['challenge_key']

reqmsg = messages.phone_check_resp
reqmsg['header']['deviceID'] = DEVICE_ID2
reqmsg['header']['hash'] = HASH2
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['username'] = USERNAME2
reqmsg['sender']['responseKey'] = response_key
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
uid2 = objs['data']['userID']

#AnandR: Should check when the response_key doesnt match the sent response_key

reqmsg = messages.phone_check_req
reqmsg['header']['deviceID'] = DEVICE_ID3
reqmsg['header']['hash'] = HASH3
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['username'] = USERNAME3
reqmsg['sender']['target'] = messages.PHONE3
reqmsg['sender']['responseMode'] = 'sms'
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
response_key = objs['data']['challenge_key']


#resp = objs['data']['key']
reqmsg = messages.phone_check_resp
reqmsg['header']['deviceID'] = DEVICE_ID3
reqmsg['header']['hash'] = HASH3
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['username'] = USERNAME3
reqmsg['sender']['responseKey'] = response_key
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
uid3 = objs['data']['userID']

reqmsg = messages.login
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['username'] = USERNAME1
reqmsg['sender']['userID'] = uid1
reqmsg['header']['deviceID'] = DEVICE_ID1
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
wuid1 = objs['data']['wizUserID']

reqmsg['sender']['username'] = USERNAME2
reqmsg['sender']['userID'] = uid2
reqmsg['header']['deviceID'] = DEVICE_ID2
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
wuid2 = objs['data']['wizUserID']

reqmsg['sender']['username'] = USERNAME3
reqmsg['sender']['userID'] = uid3
reqmsg['header']['deviceID'] = DEVICE_ID3
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
wuid3 = objs['data']['wizUserID']

#send register

#create 3 users
reqmsg = messages.register1
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID']=uid1
reqmsg['sender']['wizUserID']=wuid1
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.register2
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID']=uid2
reqmsg['sender']['wizUserID']=wuid2
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.register3
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID']=uid3
reqmsg['sender']['wizUserID']=wuid3
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])


reqmsg = messages.edit_card1
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
contacts = reqmsg['sender']['contact_container']
#populate file
for c in contacts:
    c['f_bizCardImage'] = cc_out
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
e1_id = objs['data']['wizCardID']

reqmsg = messages.edit_card2
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid2
reqmsg['sender']['wizUserID'] = wuid2
contacts = reqmsg['sender']['contact_container']
#populate file
for c in contacts:
    c['f_bizCardImage'] = cc_out
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
e2_id = objs['data']['wizCardID']

reqmsg = messages.get_email_template
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
#send_request(conn, reqmsg)
#objs = handle_response(conn, reqmsg['header']['msgType'])
#email = objs['data']['emailTemplate']
print "Email check..."

reqmsg = messages.edit_card3
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
contacts = reqmsg['sender']['contact_container']
#populate file
for c in contacts:
    c['f_bizCardImage'] = cc_out
    #c['b_bizCardImage'] = out
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
e3_id = objs['data']['wizCardID']

#send location update
reqmsg = messages.location
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['lat'] = messages.LAT1
reqmsg['sender']['lng'] = messages.LNG1
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

#send get cards to seed location information
reqmsg = messages.get_cards
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
notif = NotifParser(objs['data'], uid1, wuid1)
nrsp = notif.process()

reqmsg = messages.get_cards
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid2
reqmsg['sender']['wizUserID'] = wuid2
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
notif = NotifParser(objs['data'], uid2, wuid2)
nrsp = notif.process()

reqmsg = messages.get_cards
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
notif = NotifParser(objs['data'], uid3, wuid3)
nrsp = notif.process()

#contacts upload user 1
reqmsg = messages.contacts_upload
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['receiver']['prefix'] = INDIA_INTERNATIONAL_PREFIX
reqmsg['receiver']['country_code'] = INDIA_COUNTRY_CODE
reqmsg['receiver']['ab_list'] = messages.USER1_AB
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

#contacts upload user 2
reqmsg = messages.contacts_upload
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid2
reqmsg['sender']['wizUserID'] = wuid2
reqmsg['receiver']['prefix'] = INDIA_INTERNATIONAL_PREFIX
reqmsg['receiver']['country_code'] = INDIA_COUNTRY_CODE
reqmsg['receiver']['ab_list'] = messages.USER2_AB
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.card_details
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['receiver']['wizCardID'] = e1_id
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.card_details
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid2
reqmsg['sender']['wizUserID'] = wuid2
reqmsg['receiver']['wizCardID'] = e2_id
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.card_details
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
reqmsg['receiver']['wizCardID'] = e3_id
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])


#1:1 Tests

#assetToXYZ tests
#asset types: wizcard, table
#receiverType: phone, email, wizUserID

#u1 -> u2, u3 via wiz
reqmsg = messages.send_asset_to_xyz
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['sender']['assetID'] = e1_id
reqmsg['sender']['assetType'] = "wizcard"
reqmsg['receiver']['receiverType'] = "wiz_untrusted"
reqmsg['receiver']['receiverIDs'] = [wuid2, wuid3]
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

        # connection state so far
        # uid1(A)<->uid2(P)
        # uid1(A)<->uid3(P)

#u1 -> future_u1, u2 via sms
reqmsg = messages.send_asset_to_xyz
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['sender']['assetID'] = e1_id
reqmsg['sender']['assetType'] = "wizcard"
reqmsg['receiver']['receiverType'] = "sms"
reqmsg['receiver']['receiverIDs'] = [messages.FUTURE_PHONE1, messages.FUTURE_PHONE2]
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

#u2 -> future u1, u2 via email
reqmsg['sender']['userID'] = uid2
reqmsg['sender']['assetType'] = "wizcard"
reqmsg['sender']['wizUserID'] = wuid2
reqmsg['sender']['assetID'] = e2_id
reqmsg['receiver']['receiverType'] = "email"
reqmsg['receiver']['receiverIDs'] = [messages.FUTURE_EMAIL1, messages.FUTURE_EMAIL2]
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

#now create future u1 and u2

print "creating future user 1 and 2"
reqmsg = messages.phone_check_req
reqmsg['header']['version'] = APP_VERSION
reqmsg['header']['deviceID'] = DEVICE_ID4
reqmsg['header']['hash'] = HASH2
reqmsg['sender']['username'] = messages.FUTURE_USERNAME1
reqmsg['sender']['target'] = messages.FUTURE_PHONE1
reqmsg['sender']['responseMode'] = 'sms'

send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
response_key = objs['data']['challenge_key']

reqmsg = messages.phone_check_resp
reqmsg['header']['version'] = APP_VERSION
reqmsg['header']['deviceID'] = DEVICE_ID4
reqmsg['header']['hash'] = HASH2
reqmsg['sender']['username'] = messages.FUTURE_USERNAME1
reqmsg['sender']['responseKey'] = response_key
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
fuid1 = objs['data']['userID']


reqmsg = messages.phone_check_req
reqmsg['header']['version'] = APP_VERSION
reqmsg['header']['deviceID'] = DEVICE_ID5
reqmsg['header']['hash'] = HASH2
reqmsg['sender']['username'] = messages.FUTURE_USERNAME2
reqmsg['sender']['target'] = messages.FUTURE_PHONE2
reqmsg['sender']['responseMode'] = 'sms'

send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
response_key = objs['data']['challenge_key']

reqmsg = messages.phone_check_resp
reqmsg['header']['version'] = APP_VERSION
reqmsg['header']['deviceID'] = DEVICE_ID5
reqmsg['header']['hash'] = HASH2
reqmsg['sender']['username'] = messages.FUTURE_USERNAME2
reqmsg['sender']['responseKey'] = response_key
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
fuid2 = objs['data']['userID']

print "logging in future user 1 and 2"
reqmsg = messages.login
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['username'] = messages.FUTURE_USERNAME1
reqmsg['sender']['userID'] = fuid1
reqmsg['header']['deviceID'] = DEVICE_ID4
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
fwuid1 = objs['data']['wizUserID']

reqmsg['sender']['username'] = messages.FUTURE_USERNAME2
reqmsg['sender']['userID'] = fuid2
reqmsg['header']['deviceID'] = DEVICE_ID5
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
fwuid2 = objs['data']['wizUserID']

print "registering future user 1 and 2"
reqmsg = messages.register1
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID']=fuid1
reqmsg['sender']['wizUserID']=fwuid1
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.register2
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID']=fuid2
reqmsg['sender']['wizUserID']=fwuid2
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

print "creating wizcard for future user"
reqmsg = messages.edit_card1
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = fuid1
reqmsg['sender']['wizUserID'] = fwuid1
reqmsg['sender']['email'] = messages.FUTURE_EMAIL1
reqmsg['sender']['phone1'] = messages.FUTURE_PHONE1
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
fe1_id = objs['data']['wizCardID']

reqmsg = messages.edit_card1
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = fuid2
reqmsg['sender']['wizUserID'] = fwuid2
reqmsg['sender']['email'] = messages.FUTURE_EMAIL2
reqmsg['sender']['phone1'] = messages.FUTURE_PHONE2
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
fe2_id = objs['data']['wizCardID']


        # connection state so far
        # uid1(A)<->uid2(P)
        # uid1(A)<->uid3(P)
        # uid1(A)<->fuid1(P)
        # uid1(A)<->fuid2(P)

#at this point there should be notifs for this user
reqmsg = messages.get_cards
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
notif = NotifParser(objs['data'], uid1, wuid1)
nrsp = notif.process()

reqmsg = messages.get_cards
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid2
reqmsg['sender']['wizUserID'] = wuid2
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

notif = NotifParser(objs['data'], uid2, wuid2)
nrsp = notif.process()

reqmsg = messages.get_cards
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

notif = NotifParser(objs['data'], uid3, wuid3)
nrsp = notif.process()

reqmsg = messages.get_cards
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = fuid1
reqmsg['sender']['wizUserID'] = fwuid1
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
notif = NotifParser(objs['data'], fuid1, fwuid1)
nrsp = notif.process()

reqmsg = messages.get_cards
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = fuid2
reqmsg['sender']['wizUserID'] = fwuid2
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
notif = NotifParser(objs['data'], fuid2, fwuid2)
nrsp = notif.process()


        # connection state so far
        # uid1(A)<->uid2(P)
        # uid1(A)<->uid3(P)
        # uid1(A)<->fuid1(P)
        # uid1(A)<->fuid2(P)

# uid2 accept uid1
reqmsg = messages.accept_connection_request
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid2
reqmsg['sender']['wizUserID'] = wuid2
reqmsg['receiver']['wizUserID'] = wuid1
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

        # uid1(A)<->uid2(A)
        # uid1(A)<->uid3(P)
        # uid1(A)<->fuid1(P)
        # uid1(A)<->fuid2(P)

# uid3 decline uid1
reqmsg = messages.decline_connection_request
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
reqmsg['receiver']['wizCardID'] = e1_id
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

        # uid1(A)<->uid2(A)
        # uid1(A)<->uid3(D)
        # uid1(A)<->fuid1(P)
        # uid1(A)<->fuid2(P)

# fuid1 accept
reqmsg = messages.accept_connection_request
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = fuid1
reqmsg['sender']['wizUserID'] = fwuid1
reqmsg['receiver']['wizUserID'] = wuid1
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

        # uid1(A)<->uid2(A)
        # uid1(A)<->uid3(D)
        # uid1(A)<->fuid1(A)
        # uid1(A)<->fuid2(P)

# fuid2 decline
reqmsg = messages.decline_connection_request
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = fuid2
reqmsg['sender']['wizUserID'] = fwuid2
reqmsg['receiver']['wizCardID'] = e1_id
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

        # uid1(A)<->uid2(A)
        # uid1(A)<->uid3(D)
        # uid1(A)<->fuid1(A)
        # uid1(A)<->fuid2(D)

#u1 delete U2 rolodex
reqmsg = messages.delete_rolodex_card
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['receiver']['wizCardIDs'] = map(lambda x: {"wizCardID": x, "dead_card":False}, [e2_id])
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

        # uid1->uid2(A)
        # uid1(A)<->uid3(D)
        # uid1(A)<->fuid1(P)
        # uid1(A)<->fuid2(D)

#u1 reaccept U2
reqmsg = messages.accept_connection_request
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['sender']['reaccept'] = True
reqmsg['receiver']['wizUserID'] = wuid2
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

        # uid1(A)<->uid2(A)
        # uid1(A)<->uid3(D)
        # uid1(A)<->fuid1(A)
        # uid1(A)<->fuid2(D)

#u3 reaccept u1
reqmsg = messages.accept_connection_request
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
reqmsg['sender']['reaccept'] = True
reqmsg['receiver']['wizUserID'] = wuid1
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

        # uid1(A)<->uid2(A)
        # uid1(A)<->uid3(A)
        # uid1(A)<->fuid1(A)
        # uid1(A)<->fuid2(D)

# u1 delete U2 Rolodex
reqmsg = messages.delete_rolodex_card
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['receiver']['wizCardIDs'] = map(lambda x: {"wizCardID": x, "dead_card":False}, [e2_id])
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

        # uid1->uid2(A)
        # uid1(A)<->uid3(A)
        # uid1(A)<->fuid1(A)
        # uid1(A)<->fuid2(D)

# u1 <-> U2
reqmsg = messages.send_asset_to_xyz
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['sender']['assetID'] = e1_id
reqmsg['sender']['assetType'] = "wizcard"
reqmsg['receiver']['receiverType'] = "wiz_untrusted"
reqmsg['receiver']['receiverIDs'] = [wuid2]
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

        # uid1->uid2(A)
        # uid1(A)<->uid3(A)
        # uid1(A)<->fuid1(A)
        # uid1(A)<->fuid2(D)

#U2 delete U1 rolodex
reqmsg = messages.delete_rolodex_card
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid2
reqmsg['sender']['wizUserID'] = wuid2
reqmsg['receiver']['wizCardIDs'] = map(lambda x: {"wizCardID": x, "dead_card":False}, [e1_id])
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

        # uid1(A)<->uid3(A)
        # uid1(A)<->fuid1(A)
        # uid1(A)<->fuid2(D)

# u1 invite fuid1 when connected
reqmsg = messages.send_asset_to_xyz
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['sender']['assetID'] = e1_id
reqmsg['sender']['assetType'] = "wizcard"
reqmsg['receiver']['receiverType'] = "sms"
reqmsg['receiver']['receiverIDs'] = [messages.FUTURE_PHONE1]
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

        # uid1(A)<->uid3(A)
        # uid1(A)<->fuid1(A)
        # uid1(A)<->fuid2(D)

# u1 delete card fuid2
reqmsg = messages.delete_rolodex_card
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['receiver']['wizCardIDs'] = map(lambda x: {"wizCardID": x, "dead_card":False}, [fe2_id])
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

        # uid1(A)<->uid3(A)
        # uid1(A)<->fuid1(A)
        # uid1->fuid2(D)

# u1 invite fuid2 when declined
reqmsg = messages.send_asset_to_xyz
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['sender']['assetID'] = e1_id
reqmsg['sender']['assetType'] = "wizcard"
reqmsg['receiver']['receiverType'] = "sms"
reqmsg['receiver']['receiverIDs'] = [messages.FUTURE_PHONE2]
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

        # uid1(A)<->uid3(A)
        # uid1(A)<->fuid1(A)
        # uid1(A)<->fuid2(D)

# fuid2 accept u1
reqmsg = messages.accept_connection_request
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = fuid2
reqmsg['sender']['wizUserID'] = fwuid2
reqmsg['receiver']['wizUserID'] = wuid1
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

        # uid1(A)<->uid3(A)
        # uid1(A)->fuid1(A)
        # uid1(A)<->fuid2(A)

#delete rolodex card for u1
print "deleting all cards of ", uid1
reqmsg = messages.delete_rolodex_card
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['receiver']['wizCardIDs'] = map(lambda x: {"wizCardID": x, "dead_card":False}, [e2_id, e3_id, fe1_id, fe2_id])
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

        # uid1(A)->uid3(A)
        # uid1->fuid1(P)
        # uid1->fuid2(D)

#user query
reqmsg = messages.user_query
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
reqmsg['receiver']['name'] = FIRSTNAME_Q
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

# archived cards
reqmsg = messages.archived_cards
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

# Meishi
reqmsg = messages.meishi_start
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid2
reqmsg['sender']['wizUserID'] = wuid2
reqmsg['sender']['wizCardID'] = e1_id
reqmsg['sender']['lat'] = messages.LAT1
reqmsg['sender']['lng'] = messages.LNG1
send_request(conn, reqmsg)
objs = handle_response(conn,reqmsg['header']['msgType'])
mei_id2 = objs['data']['mID']
m_nearby = objs['data']['m_nearby']

reqmsg = messages.meishi_find
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid2
reqmsg['sender']['wizUserID'] = wuid2
reqmsg['sender']['mID'] = mei_id2
send_request(conn, reqmsg)
objs = handle_response(conn,reqmsg['header']['msgType'])
if objs['data'].has_key('m_result'):
    mei_pair = objs['data']['m_result']
else:
    # expect nearby response
    m_nearby = objs['data']['m_nearby']


#clean all rolodexes


# Table Tests
if TEST_TABLE:



    reqmsg = messages.table_create
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid1
    reqmsg['sender']['wizUserID'] = wuid1
    reqmsg['sender']['table_name'] = TABLE1NAME
    reqmsg['sender']['timeout'] = 1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])
    tid_1 = objs['data']['tableID']

    reqmsg = messages.table_create
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid2
    reqmsg['sender']['wizUserID'] = wuid2
    reqmsg['sender']['table_name'] = TABLE2NAME
    reqmsg['sender']['timeout'] = 5
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])
    tid_2 = objs['data']['tableID']

    #join created table
    print "Joining Table"
    reqmsg = messages.table_join
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid2
    reqmsg['sender']['wizUserID'] = wuid2
    reqmsg['sender']['tableID'] = tid_1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])

    print "Joining Table with error password"
    reqmsg = messages.table_join
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid3
    reqmsg['sender']['wizUserID'] = wuid3
    reqmsg['sender']['tableID'] = tid_1
    reqmsg['sender']['password'] = "xxx"
    # Parse and dump the JSON response from server
    send_request(conn, reqmsg)
    objs = handle_response(conn, reqmsg['header']['msgType'])

    print "Edit Table"
    reqmsg = messages.table_edit
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid1
    reqmsg['sender']['wizUserID'] = wuid1
    reqmsg['sender']['tableID'] = tid_1
    reqmsg['sender']['oldName'] = TABLE1NAME
    reqmsg['sender']['newName'] = TABLE1NAME_NEW
    reqmsg['sender']['timeout'] = 5
    # Parse and dump the JSON response from server
    send_request(conn, reqmsg)
    objs = handle_response(conn, reqmsg['header']['msgType'])

    print "Creating Table Three"
    reqmsg = messages.table_create
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid3
    reqmsg['sender']['wizUserID'] = wuid3
    reqmsg['sender']['table_name'] = TABLE3NAME
    reqmsg['sender']['timeout'] = 5
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])
    tid_3 = objs['data']['tableID']

    #table query
    print "sending table query"
    reqmsg = messages.table_query
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid3
    reqmsg['sender']['wizUserID'] = wuid3
    reqmsg['receiver']['name'] = TABLENAME_Q
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])

    #table summary
    print "sending table summary"
    reqmsg = messages.table_summary
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid3
    reqmsg['sender']['wizUserID'] = wuid3
    reqmsg['sender']['tableID'] = tid_2
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])

    #table details
    print "sending table details"
    reqmsg = messages.table_details
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid3
    reqmsg['sender']['wizUserID'] = wuid3
    reqmsg['sender']['tableID'] = tid_1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])


    #u1 -> u2, u3 via wiz, assetType = Table
    reqmsg = messages.send_asset_to_xyz
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid1
    reqmsg['sender']['wizUserID'] = wuid1
    reqmsg['sender']['assetID'] = tid_1
    reqmsg['sender']['assetType'] = "table"
    reqmsg['receiver']['receiverType'] = "wiz_trusted"
    reqmsg['receiver']['receiverIDs'] = [uid2, uid3]
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])


    #t1 -> fu3, fu4 via email, assetType = Table
    reqmsg = messages.send_asset_to_xyz
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid1
    reqmsg['sender']['wizUserID'] = wuid1
    reqmsg['sender']['assetID'] = tid_1
    reqmsg['sender']['assetType'] = "table"
    reqmsg['receiver']['receiverType'] = "email"
    reqmsg['receiver']['receiverIDs'] = [messages.FUTURE_EMAIL3, messages.FUTURE_EMAIL4]
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])

    #t2 -> fu3, fu4 via sms, assetType = Table
    reqmsg = messages.send_asset_to_xyz
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid2
    reqmsg['sender']['wizUserID'] = wuid2
    reqmsg['sender']['assetID'] = tid_2
    reqmsg['sender']['assetType'] = "table"
    reqmsg['receiver']['receiverType'] = "sms"
    reqmsg['receiver']['receiverIDs'] = [messages.FUTURE_PHONE3, messages.FUTURE_PHONE4]
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])

# Flick Tests

if TEST_FLICK:
    reqmsg = messages.card_flick
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid1
    reqmsg['sender']['wizUserID'] = wuid1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])
    cf1_id = objs['data']['flickCardID']

    #re flick to check agglomeration
    reqmsg = messages.card_flick
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid2
    reqmsg['sender']['wizUserID'] = wuid2
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])
    cf2_id = objs['data']['flickCardID']

    #re flick to check agglomeration with delta lat,lng
    reqmsg = messages.card_flick
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid1
    reqmsg['sender']['wizUserID'] = wuid1
    print "re-flicking card from close-by location", reqmsg['sender']['userID']
    reqmsg['sender']['lng'] += 0.000001
    reqmsg['sender']['lat'] += 0.000001
    reqmsg['sender']['timeout'] = 2
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])
    cf3_id = objs['data']['flickCardID']
    if cf3_id != cf1_id:
        print "ERROR in DELTA AGGLORMERATION"


    #edit flick
    reqmsg = messages.card_flick_edit
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid1
    reqmsg['sender']['wizUserID'] = wuid1
    reqmsg['sender']['flickCardID'] = cf1_id
    reqmsg['sender']['timeout'] = 1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])

    reqmsg = messages.card_flick
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid3
    reqmsg['sender']['wizUserID'] = wuid3
    reqmsg['sender']['timeout'] = 3
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])
    cf3_id = objs['data']['flickCardID']

    reqmsg = messages.card_flick_accept
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid1
    reqmsg['sender']['wizUserID'] = wuid1
    reqmsg['receiver']['flickCardIDs'] = [cf3_id]
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])

    reqmsg = messages.flick_pickers
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid3
    reqmsg['sender']['wizUserID'] = wuid3
    reqmsg['sender']['flickCardID'] = cf3_id
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])


    reqmsg = messages.my_flicks
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid1
    reqmsg['sender']['wizUserID'] = wuid1
    reqmsg['sender']['wizCardID'] = e1_id
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])

    reqmsg = messages.my_flicks
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid3
    reqmsg['sender']['wizUserID'] = wuid3
    reqmsg['sender']['wizCardID'] = e3_id
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])

    #flick query
    reqmsg = messages.card_flick_query
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid3
    reqmsg['sender']['wizUserID'] = wuid3
    reqmsg['receiver']['name'] = FIRSTNAME_Q
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])

if OCR_FLAG:
    #OCR USER
    reqmsg = messages.phone_check_req
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['header']['deviceID'] = DEVICE_ID3
    reqmsg['header']['hash'] = HASH3
    reqmsg['sender']['username'] = messages.OCR_USERNAME
    reqmsg['sender']['target'] = messages.OCR_PHONE
    reqmsg['sender']['responseMode'] = 'sms'
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])
    response_key = objs['data']['challenge_key']

    #resp = objs['data']['key']
    reqmsg = messages.phone_check_resp
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['header']['deviceID'] = DEVICE_ID3
    reqmsg['header']['hash'] = HASH3
    reqmsg['sender']['username'] = messages.OCR_USERNAME
    reqmsg['sender']['responseKey'] = response_key
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])
    ocr_uid = objs['data']['userID']

    reqmsg = messages.login
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['username'] = messages.OCR_USERNAME
    reqmsg['sender']['userID'] = ocr_uid
    reqmsg['header']['deviceID'] = DEVICE_ID3
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])
    ocr_wuid = objs['data']['wizUserID']

    reqmsg = messages.ocr_req_self
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = ocr_uid
    reqmsg['sender']['wizUserID'] = ocr_wuid
    reqmsg['sender']['f_ocrCardImage'] = ocr_out
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])
    contact_container = objs['data']['ocr_result']['contact_container']

    reqmsg = messages.edit_card2
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = ocr_uid
    reqmsg['sender']['wizUserID'] = ocr_wuid
    contacts = contact_container
    #populate file
    for c in contacts:
        c['f_bizCardImage'] = cc_out
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])
    ocr_wizcard_id = objs['data']['wizCardID']

    reqmsg = messages.ocr_dead_card
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid1
    reqmsg['sender']['wizUserID'] = wuid1
    reqmsg['sender']['wizCardID'] = e1_id
    reqmsg['sender']['f_ocrCardImage'] = ocr_out
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])
    dc1_id = objs['data']['response']['id']

    reqmsg = messages.ocr_dead_card_edit
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid1
    reqmsg['sender']['wizUserID'] = wuid1
    reqmsg['sender']['deadCardID'] = dc1_id
    reqmsg['sender']['inviteother'] = 1
    reqmsg['sender']['contact_container'][0]['email'] = 'anandramani98@gmail.com'
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])

    reqmsg = messages.delete_rolodex_card
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['userID'] = uid1
    reqmsg['sender']['wizUserID'] = wuid1
    reqmsg['receiver']['wizCardIDs'] = map(lambda x: {"wizCardID": x, "dead_card": True}, [dc1_id])
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])


if TEST_WIZWEB:
    ####wizweb messages########################
    #query user
    print "wizweb query existing user"
    reqmsg = messages.wizweb_query_user
    reqmsg['header']['version'] = APP_VERSION
    #reqmsg['sender']['username'] = USERNAME1
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])


    print "wizweb query non-existing user"
    reqmsg['sender']['username'] = "does not exist"
    print "wizweb message query_user ", reqmsg['sender']['username']
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])


    #query wizcard
    print "wizweb query existing wizcard"
    reqmsg = messages.wizweb_query_wizcard
    reqmsg['header']['version'] = APP_VERSION
    #reqmsg['sender']['username'] = USERNAME1
    reqmsg['sender']['userID'] = uid1
    print "wizweb message query_wizcard ", reqmsg['sender']['username']
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])

    print "wizweb query non-valid wizcard"
    reqmsg['sender']['username'] = USERNAME1
    reqmsg['sender']['userID'] = uid2
    print "wizweb message query invalid wizcard ", reqmsg['sender']['userID']
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])

    #wizweb user create
    print "wizweb user create"
    reqmsg = messages.wizweb_create_user
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['username'] = USERNAME4
    reqmsg['sender']['first_name'] = USERNAME4_FIRST_NAME
    reqmsg['sender']['last_name'] = USERNAME4_LAST_NAME
    print "wizweb message user create ", reqmsg['sender']['username']
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])
    uid4 = objs['data']['userID']

    #wizweb add card new
    print "wizweb add card latest"
    reqmsg = messages.wizweb_add_edit_card
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['username'] = USERNAME4
    reqmsg['sender']['userID'] = uid4
    reqmsg['sender']['mode'] = 1
    reqmsg['sender']['first_name'] = USERNAME4_FIRST_NAME
    reqmsg['sender']['last_name'] = USERNAME4_LAST_NAME
    reqmsg['sender']['phone'] = messages.PHONE4
    reqmsg['sender']['title'] = DEFAULT_TITLE
    reqmsg['sender']['company'] = DEFAULT_COMPANY
    reqmsg['sender']['start'] = START1
    reqmsg['sender']['mediaUrl'] = DEFAULT_MEDIA_URL
    reqmsg['sender']['f_bizCardUrl'] = DEFAULT_BIZCARD_URL
    print "wizweb message edit card latest ", reqmsg['sender']['userID']
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])

    #wizweb edit card
    print "wizweb edit card force"
    reqmsg = messages.wizweb_add_edit_card
    reqmsg['header']['version'] = APP_VERSION
    reqmsg['sender']['username'] = USERNAME1
    reqmsg['sender']['userID'] = uid1
    reqmsg['sender']['mode'] = 2
    reqmsg['sender']['first_name'] = USERNAME1
    reqmsg['sender']['last_name'] = USERNAME1
    reqmsg['sender']['phone'] = messages.PHONE1
    reqmsg['sender']['title'] = DEFAULT_TITLE
    reqmsg['sender']['company'] = DEFAULT_COMPANY
    reqmsg['sender']['start'] = START1
    reqmsg['sender']['mediaUrl'] = DEFAULT_MEDIA_URL
    reqmsg['sender']['f_bizCardUrl'] = DEFAULT_BIZCARD_URL
    print "wizweb message edit card force ", reqmsg['sender']['userID']
    send_request(conn, reqmsg)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])

#DELETE_ROLODEX_CASE

reqmsg = messages.phone_check_req
reqmsg['header']['deviceID'] = DEVICE_ID1
reqmsg['header']['hash'] = HASH1
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['username'] = DELETE_ROLODEX_USER1
reqmsg['sender']['target'] = messages.NEXMO_PHONE1
reqmsg['sender']['responseMode'] = 'sms'
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
response_key = objs['data'].get('challenge_key', 1234)

reqmsg = messages.phone_check_resp
reqmsg['header']['deviceID'] = DEVICE_ID1
reqmsg['header']['hash'] = HASH1
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['username'] = DELETE_ROLODEX_USER1
reqmsg['sender']['responseKey'] = response_key
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
uid1 = objs['data']['userID']

reqmsg = messages.login
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['username'] = DELETE_ROLODEX_USER1
reqmsg['sender']['userID'] = uid1
reqmsg['header']['deviceID'] = DEVICE_ID1
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
wuid1 = objs['data']['wizUserID']



reqmsg = messages.phone_check_req
reqmsg['header']['deviceID'] = DEVICE_ID2
reqmsg['header']['hash'] = HASH1
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['username'] = DELETE_ROLODEX_USER2
reqmsg['sender']['target'] = messages.NEXMO_PHONE1
reqmsg['sender']['responseMode'] = 'sms'
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
response_key = objs['data'].get('challenge_key', 1234)

reqmsg = messages.phone_check_resp
reqmsg['header']['deviceID'] = DEVICE_ID2
reqmsg['header']['hash'] = HASH1
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['username'] = DELETE_ROLODEX_USER2
reqmsg['sender']['responseKey'] = response_key
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
uid2 = objs['data']['userID']

reqmsg = messages.login
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['username'] = DELETE_ROLODEX_USER2
reqmsg['sender']['userID'] = uid2
reqmsg['header']['deviceID'] = DEVICE_ID2
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
wuid2 = objs['data']['wizUserID']

reqmsg = messages.phone_check_req
reqmsg['header']['deviceID'] = DEVICE_ID3
reqmsg['header']['hash'] = HASH1
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['username'] = DELETE_ROLODEX_USER3
reqmsg['sender']['target'] = messages.NEXMO_PHONE1
reqmsg['sender']['responseMode'] = 'sms'
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
response_key = objs['data'].get('challenge_key', 1234)

reqmsg = messages.phone_check_resp
reqmsg['header']['deviceID'] = DEVICE_ID3
reqmsg['header']['hash'] = HASH1
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['username'] = DELETE_ROLODEX_USER3
reqmsg['sender']['responseKey'] = response_key
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
uid3 = objs['data']['userID']

reqmsg = messages.login
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['username'] = DELETE_ROLODEX_USER3
reqmsg['sender']['userID'] = uid3
reqmsg['header']['deviceID'] = DEVICE_ID3
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
wuid3 = objs['data']['wizUserID']

reqmsg = messages.register1
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID']=uid1
reqmsg['sender']['wizUserID']=wuid1
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.register2
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID']=uid2
reqmsg['sender']['wizUserID']=wuid2
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.register3
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID']=uid3
reqmsg['sender']['wizUserID']=wuid3
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.rolodex_edit_card1
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
contacts = reqmsg['sender']['contact_container']
#populate file
for c in contacts:
    c['f_bizCardImage'] = cc_out
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
e1_id = objs['data']['wizCardID']

reqmsg = messages.rolodex_edit_card2
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid2
reqmsg['sender']['wizUserID'] = wuid2
contacts = reqmsg['sender']['contact_container']
#populate file
for c in contacts:
    c['f_bizCardImage'] = cc_out
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
e2_id = objs['data']['wizCardID']

reqmsg = messages.rolodex_edit_card3
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
contacts = reqmsg['sender']['contact_container']
#populate file
for c in contacts:
    c['f_bizCardImage'] = cc_out
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
e3_id = objs['data']['wizCardID']

reqmsg = messages.send_asset_to_xyz
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['sender']['assetID'] = e1_id
reqmsg['sender']['assetType'] = "wizcard"
reqmsg['receiver']['receiverType'] = "wiz_untrusted"
reqmsg['receiver']['receiverIDs'] = [wuid2, wuid3]
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

# send get cards to clear readed on one guy
reqmsg = messages.get_cards
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid2
reqmsg['sender']['wizUserID'] = wuid2
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

# delete. Expect 3 to go back to new state, and 2 will follow error 24 path upon
# accept/decline
reqmsg = messages.delete_rolodex_card
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['receiver']['wizCardIDs'] = map(lambda x: {"wizCardID": x, "dead_card":False}, [e2_id, e3_id])
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])


# uid2 accept uid1
reqmsg = messages.accept_connection_request
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid2
reqmsg['sender']['wizUserID'] = wuid2
reqmsg['receiver']['wizUserID'] = wuid1
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])


# recreate 1<->3 to test decline path
reqmsg = messages.send_asset_to_xyz
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['sender']['assetID'] = e1_id
reqmsg['sender']['assetType'] = "wizcard"
reqmsg['receiver']['receiverType'] = "wiz_untrusted"
reqmsg['receiver']['receiverIDs'] = [wuid3]
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

# send get cards to clear readed on 3
reqmsg = messages.get_cards
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.delete_rolodex_card
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['receiver']['wizCardIDs'] = map(lambda x: {"wizCardID": x, "dead_card":False}, [e3_id])
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

#uid3 declines uid1
reqmsg = messages.decline_connection_request
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
reqmsg['receiver']['wizCardID'] = e1_id
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
