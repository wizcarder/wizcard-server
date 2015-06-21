#!/usr/bin/python

# Test WizCard client (the real one resides on a smartphone - iphone, android)

# Standard imports
import httplib
import json
import pdb
import messages
from notifications import NotifParser
import random
import string

#1 Flick
#2 flick
#3 flick

#1 - 3 Connected


#T1 - [u1, u2]

#1 - 2 Connected

#T2 - [u2]
#T3 - [u3]

#delete rolodex - 1



TEST_IMAGE=True
OCR_FLAG = True

NEXMO_PHONE1 = "14084641727"
PHONE1 = "14084641727"
PHONE2 = "+15085332708"
PHONE3 = "+15086892263"
PHONE4 = "+15086892263"
PHONE5 = "+11086892263"
PHONE6 = "+12086892263"

FUTURE_PHONE1 = "+11111111111"
FUTURE_PHONE2 = "+12222222222"
FUTURE_PHONE3 = "+13333333333"
FUTURE_PHONE4 = "+14444444444"
FUTURE_USERNAME1 = FUTURE_PHONE1+'@wizcard.com'
FUTURE_USERNAME2 = FUTURE_PHONE2+'@wizcard.com'
FUTURE_USERNAME3 = FUTURE_PHONE3+'@wizcard.com'
FUTURE_USERNAME4 = FUTURE_PHONE4+'@wizcard.com'
FUTURE_EMAIL1 = "abcd@future.com"
FUTURE_EMAIL2 = "efgh@future.com"
FUTURE_EMAIL3 = "ijkl@future.com"
FUTURE_EMAIL4 = "mnop@future.com"

EMAIL1 = "aammundi@gmail.com"
EMAIL2 = "amsaha@gmail.com"
EMAIL3 = "wizcard1@gmail.com"
EMAIL4 = "nothere@gmail.com"



USERNAME1 = PHONE1+'@wizcard.com'
USERNAME2 = PHONE2+'@wizcard.com'
USERNAME3 = PHONE3+'@wizcard.com'
USERNAME4 = "wizweb_user1" + ''.join(random.choice(string.digits) for x in range(2))
USERNAME4_FIRST_NAME = "WizWeb_1"
USERNAME4_LAST_NAME = "Last_1"

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
DEVICE_ID6 = "dddddddddddddddddddddddddd"
DEVICE_ID7 = "Reeeeeeeeeeeeeeeeeeeeeeeee"


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

LAT1 = 37.885938
LNG1 = -122.506419

verify_phones_list = [PHONE1, PHONE2, PHONE3]
verify_emails_list = [EMAIL1, EMAIL2, EMAIL3, EMAIL4]

#server_url = "www.totastyle.com"
server_url = "ec2-54-219-163-35.us-west-1.compute.amazonaws.com"
#server_url = "wizserver-lb-797719134.us-west-1.elb.amazonaws.com"
#server_url = "localhost"

server_port = 8000
#server_port = 80

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
reqmsg['sender']['username'] = USERNAME1
reqmsg['sender']['target'] = NEXMO_PHONE1
reqmsg['sender']['responseMode'] = 'voice'
reqmsg['sender']['test_mode'] = True
pcreq1 = json.dumps(reqmsg)
conn.request("POST","", pcreq1)
print "sending phone_check_req", pcreq1
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
response_key = objs['data']['challenge_key']

reqmsg = messages.phone_check_resp
reqmsg['header']['deviceID'] = DEVICE_ID1
reqmsg['header']['hash'] = HASH1
reqmsg['sender']['username'] = USERNAME1
reqmsg['sender']['responseKey'] = response_key
pcrsp1 = json.dumps(reqmsg)
print "sending phone_check_rsp", pcrsp1
conn.request("POST","", pcrsp1)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
uid1 = objs['data']['userID']

reqmsg = messages.phone_check_req
reqmsg['header']['deviceID'] = DEVICE_ID2
reqmsg['header']['hash'] = HASH2
reqmsg['sender']['username'] = USERNAME2
reqmsg['sender']['target'] = PHONE2
reqmsg['sender']['responseMode'] = 'sms'
reqmsg['sender']['test_mode'] = True
pcreq2 = json.dumps(reqmsg)
conn.request("POST","", pcreq2)
print "sending phone_check_req", pcreq2
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
response_key = objs['data']['challenge_key']

reqmsg = messages.phone_check_resp
reqmsg['header']['deviceID'] = DEVICE_ID2
reqmsg['header']['hash'] = HASH2
reqmsg['sender']['username'] = USERNAME2
reqmsg['sender']['responseKey'] = response_key
pcrsp2 = json.dumps(reqmsg)
print "sending phone_check_rsp", pcrsp2
conn.request("POST","", pcrsp2)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
uid2 = objs['data']['userID']

reqmsg = messages.phone_check_req
reqmsg['header']['deviceID'] = DEVICE_ID3
reqmsg['header']['hash'] = HASH3
reqmsg['sender']['username'] = USERNAME3
reqmsg['sender']['target'] = PHONE3
reqmsg['sender']['responseMode'] = 'sms'
reqmsg['sender']['test_mode'] = True
pcreq3 = json.dumps(reqmsg)
conn.request("POST","", pcreq3)
print "sending phone_check_req", pcreq3
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
response_key = objs['data']['challenge_key']

#resp = objs['data']['key']
reqmsg = messages.phone_check_resp
reqmsg['header']['deviceID'] = DEVICE_ID3
reqmsg['header']['hash'] = HASH3
reqmsg['sender']['username'] = USERNAME3
reqmsg['sender']['responseKey'] = response_key
pcrsp3 = json.dumps(reqmsg)
print "sending phone_check_rsp", pcrsp3
conn.request("POST","", pcrsp3)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
uid3 = objs['data']['userID']

reqmsg = messages.login
reqmsg['sender']['username'] = USERNAME1
reqmsg['sender']['userID'] = uid1
reqmsg['header']['deviceID'] = DEVICE_ID1
login = json.dumps(reqmsg)
print "sending login", login
conn.request("POST","", login)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
wuid1 = objs['data']['wizUserID']

reqmsg['sender']['username'] = USERNAME2
reqmsg['sender']['userID'] = uid2
reqmsg['header']['deviceID'] = DEVICE_ID2
login = json.dumps(reqmsg)
print "sending login", login
conn.request("POST","", login)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
wuid2 = objs['data']['wizUserID']

reqmsg['sender']['username'] = USERNAME3
reqmsg['sender']['userID'] = uid3
reqmsg['header']['deviceID'] = DEVICE_ID3
login = json.dumps(reqmsg)
print "sending login", login
conn.request("POST","", login)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
wuid3 = objs['data']['wizUserID']

#send register

#create 3 users
reqmsg = messages.register1
reqmsg['sender']['userID']=uid1
reqmsg['sender']['wizUserID']=wuid1
r1 = json.dumps(reqmsg)
conn.request("POST","", r1)
print "sending register"
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.register2
reqmsg['sender']['userID']=uid2
reqmsg['sender']['wizUserID']=wuid2
r2 = json.dumps(reqmsg)
conn.request("POST","", r2)
# Parse and dump the JSON response from server
print "sending register"
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.register3
reqmsg['sender']['userID']=uid3
reqmsg['sender']['wizUserID']=wuid3
r3 = json.dumps(reqmsg)
conn.request("POST","", r3)
print "sending register"
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.edit_card1
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
contacts = reqmsg['sender']['contact_container']
#populate file
for c in contacts:
    c['f_bizCardImage'] = cc_out
e1 = json.dumps(reqmsg)
print "sending EDIT CARD for", reqmsg['sender']['userID']
conn.request("POST","", e1)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
e1_id = objs['data']['wizCardID']

reqmsg = messages.edit_card2
reqmsg['sender']['userID'] = uid2
reqmsg['sender']['wizUserID'] = wuid2
contacts = reqmsg['sender']['contact_container']
#populate file
for c in contacts:
    c['f_bizCardImage'] = cc_out
e2 = json.dumps(reqmsg)
print "sending EDIT CARD for", reqmsg['sender']['userID']
conn.request("POST","", e2)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
e2_id = objs['data']['wizCardID']

reqmsg = messages.edit_card3
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
contacts = reqmsg['sender']['contact_container']
#populate file
for c in contacts:
    c['f_bizCardImage'] = cc_out
    #c['b_bizCardImage'] = out
e3 = json.dumps(reqmsg)
print "sending EDIT CARD for", reqmsg['sender']['userID']
conn.request("POST","", e3)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
e3_id = objs['data']['wizCardID']

#send location update
reqmsg = messages.location
reqmsg['sender']['lat'] = LAT1
reqmsg['sender']['lng'] = LNG1
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
l1 = json.dumps(reqmsg)
print "sending Location Update for", reqmsg['sender']['userID']
conn.request("POST","", l1)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

#contacts verify
reqmsg = messages.contacts_verify
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['receiver']['verify_phones'] = verify_phones_list
reqmsg['receiver']['verify_emails'] = verify_emails_list
cv = json.dumps(reqmsg)
print "sending Contact Verify", reqmsg['sender']['userID']
conn.request("POST","", cv)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.card_flick
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
print "flicking card", reqmsg['sender']['userID']
cf1 = json.dumps(reqmsg)
conn.request("POST","", cf1)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
cf1_id = objs['data']['flickCardID']

#re flick to check agglomeration
reqmsg = messages.card_flick
reqmsg['sender']['userID'] = uid2
reqmsg['sender']['wizUserID'] = wuid2
print "flicking card", reqmsg['sender']['userID']
cf2 = json.dumps(reqmsg)
conn.request("POST","", cf2)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
cf2_id = objs['data']['flickCardID']

#re flick to check agglomeration with delta lat,lng
reqmsg = messages.card_flick
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
print "re-flicking card from close-by location", reqmsg['sender']['userID']
reqmsg['sender']['lng'] += 0.000001
reqmsg['sender']['lat'] += 0.000001
reqmsg['sender']['timeout'] = 2
cf3 = json.dumps(reqmsg)
conn.request("POST","", cf3)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
cf3_id = objs['data']['flickCardID']
if cf3_id != cf1_id:
    print "ERROR in DELTA AGGLORMERATION"


#edit flick
card_flick_edit_msg = messages.card_flick_edit
card_flick_edit_msg['sender']['userID'] = uid1
card_flick_edit_msg['sender']['wizUserID'] = wuid1
card_flick_edit_msg['sender']['flickCardID'] = cf1_id
card_flick_edit_msg['sender']['timeout'] = 1
cfe1 = json.dumps(card_flick_edit_msg)
conn.request("POST","", cfe1)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.card_flick
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
card_flick_edit_msg['sender']['timeout'] = 3
print "flicking card", reqmsg['sender']['userID']
cf3 = json.dumps(reqmsg)
conn.request("POST","", cf3)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
cf3_id = objs['data']['flickCardID']

print "pick up flicked card"
reqmsg = messages.card_flick_accept
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['receiver']['flickCardIDs'] = [cf3_id]
cfa1 = json.dumps(reqmsg)
conn.request("POST","", cfa1)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

print "checking flick pickers"
reqmsg = messages.flick_pickers
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
reqmsg['sender']['flickCardID'] = cf3_id
fp3 = json.dumps(reqmsg)
conn.request("POST","", fp3)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])


print "retrieving myFlicks"
reqmsg = messages.my_flicks
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['sender']['wizCardID'] = e1_id
mcf1 = json.dumps(reqmsg)
conn.request("POST","", mcf1)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.my_flicks
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
reqmsg['sender']['wizCardID'] = e3_id
mcf3 = json.dumps(reqmsg)
conn.request("POST","", mcf3)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

#user query
reqmsg = messages.user_query
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
reqmsg['receiver']['name'] = FIRSTNAME_Q
uq = json.dumps(reqmsg)
conn.request("POST","", uq)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

#flick query
reqmsg = messages.card_flick_query
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
reqmsg['receiver']['name'] = FIRSTNAME_Q
fq3 = json.dumps(reqmsg)
conn.request("POST","", fq3)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

print "Creating Table one"
reqmsg = messages.table_create
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['sender']['table_name'] = TABLE1NAME
reqmsg['sender']['timeout'] = 1
tbl_c_1 = json.dumps(reqmsg)
conn.request("POST","", tbl_c_1)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
tid_1 = objs['data']['tableID']

print "Creating Table two"
reqmsg = messages.table_create
reqmsg['sender']['userID'] = uid2
reqmsg['sender']['wizUserID'] = wuid2
reqmsg['sender']['table_name'] = TABLE2NAME
reqmsg['sender']['timeout'] = 1
tbl_c_2 = json.dumps(reqmsg)
conn.request("POST","", tbl_c_2)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
tid_2 = objs['data']['tableID']

#join created table
print "Joining Table"
reqmsg = messages.table_join
reqmsg['sender']['userID'] = uid2
reqmsg['sender']['wizUserID'] = wuid2
reqmsg['sender']['tableID'] = tid_1
tbl_j_1 = json.dumps(reqmsg)
conn.request("POST","", tbl_j_1)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

print "Joining Table with error password"
reqmsg = messages.table_join
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
reqmsg['sender']['tableID'] = tid_1
reqmsg['sender']['password'] = "xxx"
tbl_j_1 = json.dumps(reqmsg)
# Parse and dump the JSON response from server
conn.request("POST","", tbl_j_1)
objs = handle_response(conn, reqmsg['header']['msgType'])

print "Edit Table"
reqmsg = messages.table_edit
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['sender']['tableID'] = tid_1
reqmsg['sender']['oldName'] = TABLE1NAME
reqmsg['sender']['newName'] = TABLE1NAME_NEW
reqmsg['sender']['timeout'] = 5
tbl_e_1 = json.dumps(reqmsg)
# Parse and dump the JSON response from server
conn.request("POST","", tbl_e_1)
objs = handle_response(conn, reqmsg['header']['msgType'])

print "Creating Table Three"
reqmsg = messages.table_create
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
reqmsg['sender']['table_name'] = TABLE3NAME
reqmsg['sender']['timeout'] = 5
tbl_c_3 = json.dumps(reqmsg)
conn.request("POST","", tbl_c_3)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
tid_3 = objs['data']['tableID']

#table query
print "sending table query"
reqmsg = messages.table_query
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
reqmsg['receiver']['name'] = TABLENAME_Q
tq3 = json.dumps(reqmsg)
conn.request("POST","", tq3)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

#table summary
print "sending table summary"
reqmsg = messages.table_summary
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
reqmsg['sender']['tableID'] = tid_2
ts3 = json.dumps(reqmsg)
conn.request("POST","", ts3)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

#table details
print "sending table details"
reqmsg = messages.table_details
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
reqmsg['sender']['tableID'] = tid_1
td3 = json.dumps(reqmsg)
conn.request("POST","", td3)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

#delete rolodex card
print "deleting all cards of ", uid1
reqmsg = messages.delete_rolodex_card
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['receiver']['wizCardIDs'] = [e2_id, e3_id]
dc1 = json.dumps(reqmsg)
conn.request("POST","", dc1)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])


print "get cards for user", uid1
reqmsg = messages.get_cards
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
print "GET cards", reqmsg['sender']['userID']
gcu1 = json.dumps(reqmsg)
conn.request("POST","", gcu1)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

notif = NotifParser(objs['data'], uid1, wuid1)
nrsp = notif.process_one()
while nrsp != False:
    if nrsp is not None:
        nrsp = json.dumps(nrsp)
        conn.request("POST","", n)
        # Parse and dump the JSON response from server
        objs = handle_response(conn, reqmsg['header']['msgType'])
    nrsp = notif.process_one()

reqmsg = messages.card_details
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['receiver']['wizCardID'] = e1_id
print "GET card DETAILS", reqmsg['sender']['userID']
cd1 = json.dumps(reqmsg)
conn.request("POST","", cd1)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.card_details
reqmsg['sender']['userID'] = uid2
reqmsg['sender']['wizUserID'] = wuid2
reqmsg['receiver']['wizCardID'] = e2_id
print "GET card DETAILS", reqmsg['sender']['userID']
cd2 = json.dumps(reqmsg)
conn.request("POST","", cd2)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.card_details
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
reqmsg['receiver']['wizCardID'] = e3_id
print "GET card DETAILS", reqmsg['sender']['userID']
cd3 = json.dumps(reqmsg)
conn.request("POST","", cd3)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

#assetToXYZ tests
#asset types: wizcard, table
#receiverType: phone, email, wizUserID

#u1 -> u2, u3 via wiz
reqmsg = messages.send_asset_to_xyz
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['sender']['assetID'] = e1_id
reqmsg['sender']['assetType'] = "wizcard"
reqmsg['receiver']['receiverType'] = "wiz_untrusted"
reqmsg['receiver']['receiverIDs'] = [wuid2, wuid3]
print "sendingWizcardToUnTrusted"
sxyz = json.dumps(reqmsg)
conn.request("POST","", sxyz)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])


#u1 -> future_u1, u2 via sms
reqmsg = messages.send_asset_to_xyz
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['sender']['assetID'] = e1_id
reqmsg['sender']['assetType'] = "wizcard"
reqmsg['receiver']['receiverType'] = "sms"
reqmsg['receiver']['receiverIDs'] = [FUTURE_PHONE1, FUTURE_PHONE2]
print "sendingWizcardToSMS"
sxyz = json.dumps(reqmsg)
conn.request("POST","", sxyz)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

#u2 -> future u1, u2 via email
reqmsg['sender']['userID'] = uid2
reqmsg['sender']['assetType'] = "wizcard"
reqmsg['sender']['wizUserID'] = wuid2
reqmsg['sender']['assetID'] = e2_id
reqmsg['receiver']['receiverType'] = "email"
reqmsg['receiver']['receiverIDs'] = [FUTURE_EMAIL1, FUTURE_EMAIL2]
print "sendingWizcardToEMAIL"
sxyz = json.dumps(reqmsg)
conn.request("POST","", sxyz)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

#now create future u1 and u2

print "creating future user 1 and 2"
reqmsg = messages.phone_check_req
reqmsg['header']['deviceID'] = DEVICE_ID4
reqmsg['header']['hash'] = HASH2
reqmsg['sender']['username'] = FUTURE_USERNAME1
reqmsg['sender']['target'] = FUTURE_PHONE1
reqmsg['sender']['responseMode'] = 'sms'
reqmsg['sender']['test_mode'] = True
pcreq2 = json.dumps(reqmsg)
conn.request("POST","", pcreq2)
print "sending phone_check_req", pcreq2
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
response_key = objs['data']['challenge_key']

reqmsg = messages.phone_check_resp
reqmsg['header']['deviceID'] = DEVICE_ID4
reqmsg['header']['hash'] = HASH2
reqmsg['sender']['username'] = FUTURE_USERNAME1
reqmsg['sender']['responseKey'] = response_key
pcrsp2 = json.dumps(reqmsg)
print "sending phone_check_rsp", pcrsp2
conn.request("POST","", pcrsp2)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
fuid1 = objs['data']['userID']


reqmsg = messages.phone_check_req
reqmsg['header']['deviceID'] = DEVICE_ID5
reqmsg['header']['hash'] = HASH2
reqmsg['sender']['username'] = FUTURE_USERNAME2
reqmsg['sender']['target'] = FUTURE_PHONE2
reqmsg['sender']['responseMode'] = 'sms'
reqmsg['sender']['test_mode'] = True
pcreq2 = json.dumps(reqmsg)
conn.request("POST","", pcreq2)
print "sending phone_check_req", pcreq2
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
response_key = objs['data']['challenge_key']

reqmsg = messages.phone_check_resp
reqmsg['header']['deviceID'] = DEVICE_ID5
reqmsg['header']['hash'] = HASH2
reqmsg['sender']['username'] = FUTURE_USERNAME2
reqmsg['sender']['responseKey'] = response_key
pcrsp2 = json.dumps(reqmsg)
print "sending phone_check_rsp", pcrsp2
conn.request("POST","", pcrsp2)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
fuid2 = objs['data']['userID']

print "logging in future user 1 and 2"
reqmsg = messages.login
reqmsg['sender']['username'] = FUTURE_USERNAME1
reqmsg['sender']['userID'] = fuid1
reqmsg['header']['deviceID'] = DEVICE_ID4
login = json.dumps(reqmsg)
print "sending login", login
conn.request("POST","", login)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
fwuid1 = objs['data']['wizUserID']

reqmsg['sender']['username'] = FUTURE_USERNAME2
reqmsg['sender']['userID'] = fuid2
reqmsg['header']['deviceID'] = DEVICE_ID5
login = json.dumps(reqmsg)
print "sending login", login
conn.request("POST","", login)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
fwuid2 = objs['data']['wizUserID']

print "registering future user 1 and 2"
reqmsg = messages.register1
reqmsg['sender']['userID']=fuid1
reqmsg['sender']['wizUserID']=fwuid1
r1 = json.dumps(reqmsg)
conn.request("POST","", r1)
print "sending register"
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.register2
reqmsg['sender']['userID']=fuid2
reqmsg['sender']['wizUserID']=fwuid2
r2 = json.dumps(reqmsg)
conn.request("POST","", r2)
# Parse and dump the JSON response from server
print "sending register"
objs = handle_response(conn, reqmsg['header']['msgType'])

print "creating wizcard for future user"
reqmsg = messages.edit_card1
reqmsg['sender']['userID'] = fuid1
reqmsg['sender']['wizUserID'] = fwuid1
reqmsg['sender']['email'] = FUTURE_EMAIL1
reqmsg['sender']['phone1'] = FUTURE_PHONE1
fe1 = json.dumps(reqmsg)
print "sending EDIT CARD for", reqmsg['sender']['userID']
conn.request("POST","", fe1)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
fe1_id = objs['data']['wizCardID']

reqmsg = messages.edit_card1
reqmsg['sender']['userID'] = fuid2
reqmsg['sender']['wizUserID'] = fwuid2
reqmsg['sender']['email'] = FUTURE_EMAIL2
reqmsg['sender']['phone1'] = FUTURE_PHONE2
fe2 = json.dumps(reqmsg)
print "sending EDIT CARD for", reqmsg['sender']['userID']
conn.request("POST","", fe2)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
e2_id = objs['data']['wizCardID']

#at this point there should be notifs for this user
reqmsg = messages.get_cards
reqmsg['sender']['userID'] = fuid1
reqmsg['sender']['wizUserID'] = fwuid1
print "GET cards", reqmsg['sender']['userID']
gcfu1 = json.dumps(reqmsg)
conn.request("POST","", gcfu1)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.get_cards
reqmsg['sender']['userID'] = fuid2
reqmsg['sender']['wizUserID'] = fwuid2
print "GET cards", reqmsg['sender']['userID']
gcfu2 = json.dumps(reqmsg)
conn.request("POST","", gcfu2)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

#delete rolodex card for u1
print "deleting all cards of ", uid1
reqmsg = messages.delete_rolodex_card
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['receiver']['wizCardIDs'] = [e2_id, e3_id]
dc1 = json.dumps(reqmsg)
conn.request("POST","", dc1)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

#t1 -> fu3, fu4 via email, assetType = Table
reqmsg = messages.send_asset_to_xyz
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['sender']['assetID'] = tid_1
reqmsg['sender']['assetType'] = "table"
reqmsg['receiver']['receiverType'] = "email"
reqmsg['receiver']['receiverIDs'] = [FUTURE_EMAIL3, FUTURE_EMAIL4]
print "sending table invite via email"
sxyz = json.dumps(reqmsg)
conn.request("POST","", sxyz)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

#t2 -> fu3, fu4 via sms, assetType = Table
reqmsg = messages.send_asset_to_xyz
reqmsg['sender']['userID'] = uid2
reqmsg['sender']['wizUserID'] = wuid2
reqmsg['sender']['assetID'] = tid_2
reqmsg['sender']['assetType'] = "table"
reqmsg['receiver']['receiverType'] = "sms"
reqmsg['receiver']['receiverIDs'] = [FUTURE_PHONE3, FUTURE_PHONE4]
print "sending table invite via sms"
sxyz = json.dumps(reqmsg)
conn.request("POST","", sxyz)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

#now create future u3 and u4
print "creating future user 3 and 4"
reqmsg = messages.phone_check_req
reqmsg['header']['deviceID'] = DEVICE_ID6
reqmsg['header']['hash'] = HASH2
reqmsg['sender']['username'] = FUTURE_USERNAME3
reqmsg['sender']['target'] = FUTURE_PHONE3
reqmsg['sender']['responseMode'] = 'sms'
reqmsg['sender']['test_mode'] = True
pcreq3 = json.dumps(reqmsg)
conn.request("POST","", pcreq3)
print "sending phone_check_req", pcreq3
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
response_key = objs['data']['challenge_key']

reqmsg = messages.phone_check_resp
reqmsg['header']['deviceID'] = DEVICE_ID6
reqmsg['header']['hash'] = HASH2
reqmsg['sender']['username'] = FUTURE_USERNAME3
reqmsg['sender']['responseKey'] = response_key
pcrsp3 = json.dumps(reqmsg)
print "sending phone_check_rsp", pcrsp3
conn.request("POST","", pcrsp3)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
fuid3 = objs['data']['userID']


reqmsg = messages.phone_check_req
reqmsg['header']['deviceID'] = DEVICE_ID7
reqmsg['header']['hash'] = HASH2
reqmsg['sender']['username'] = FUTURE_USERNAME4
reqmsg['sender']['target'] = FUTURE_PHONE4
reqmsg['sender']['responseMode'] = 'sms'
reqmsg['sender']['test_mode'] = True
pcreq4 = json.dumps(reqmsg)
conn.request("POST","", pcreq4)
print "sending phone_check_req", pcreq4
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
response_key = objs['data']['challenge_key']

reqmsg = messages.phone_check_resp
reqmsg['header']['deviceID'] = DEVICE_ID7
reqmsg['header']['hash'] = HASH2
reqmsg['sender']['username'] = FUTURE_USERNAME4
reqmsg['sender']['responseKey'] = response_key
pcrsp4 = json.dumps(reqmsg)
print "sending phone_check_rsp", pcrsp4
conn.request("POST","", pcrsp4)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
fuid4 = objs['data']['userID']

print "logging in future user 3 and 4"
reqmsg = messages.login
reqmsg['sender']['username'] = FUTURE_USERNAME3
reqmsg['sender']['userID'] = fuid3
reqmsg['header']['deviceID'] = DEVICE_ID6
login = json.dumps(reqmsg)
print "sending login", login
conn.request("POST","", login)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
fwuid3 = objs['data']['wizUserID']

reqmsg['sender']['username'] = FUTURE_USERNAME4
reqmsg['sender']['userID'] = fuid4
reqmsg['header']['deviceID'] = DEVICE_ID7
login = json.dumps(reqmsg)
print "sending login", login
conn.request("POST","", login)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
fwuid4 = objs['data']['wizUserID']

print "registering future user 3 and 4"
reqmsg = messages.register1
reqmsg['sender']['userID']=fuid3
reqmsg['sender']['wizUserID']=fwuid3
r3 = json.dumps(reqmsg)
conn.request("POST","", r3)
print "sending register"
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.register1
reqmsg['sender']['userID']=fuid4
reqmsg['sender']['wizUserID']=fwuid4
r4 = json.dumps(reqmsg)
conn.request("POST","", r4)
# Parse and dump the JSON response from server
print "sending register"
objs = handle_response(conn, reqmsg['header']['msgType'])

print "creating wizcard for future user"
reqmsg = messages.edit_card1
reqmsg['sender']['userID'] = fuid3
reqmsg['sender']['wizUserID'] = fwuid3
reqmsg['sender']['email'] = FUTURE_EMAIL3
reqmsg['sender']['phone1'] = FUTURE_PHONE3
fe3 = json.dumps(reqmsg)
print "sending EDIT CARD for", reqmsg['sender']['userID']
conn.request("POST","", fe3)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
fe3_id = objs['data']['wizCardID']

reqmsg = messages.edit_card1
reqmsg['sender']['userID'] = fuid4
reqmsg['sender']['wizUserID'] = fwuid4
reqmsg['sender']['email'] = FUTURE_EMAIL4
reqmsg['sender']['phone1'] = FUTURE_PHONE4
fe4 = json.dumps(reqmsg)
print "sending EDIT CARD for", reqmsg['sender']['userID']
conn.request("POST","", fe4)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
fe4_id = objs['data']['wizCardID']

#at this point there should be notifs for this user
reqmsg = messages.get_cards
reqmsg['sender']['userID'] = fuid3
reqmsg['sender']['wizUserID'] = fwuid3
print "GET cards", reqmsg['sender']['userID']
gcfu3 = json.dumps(reqmsg)
conn.request("POST","", gcfu3)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.get_cards
reqmsg['sender']['userID'] = fuid4
reqmsg['sender']['wizUserID'] = fwuid4
print "GET cards", reqmsg['sender']['userID']
gcfu4 = json.dumps(reqmsg)
conn.request("POST","", gcfu4)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])


#u1 -> u2, u3 via wiz, assetType = Table
reqmsg = messages.send_asset_to_xyz
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['sender']['assetID'] = tid_1
reqmsg['sender']['assetType'] = "table"
reqmsg['receiver']['receiverType'] = "wiz_trusted"
reqmsg['receiver']['receiverIDs'] = [wuid2, wuid3]
print "sendingWizcardToUnTrusted via table"
sxyz = json.dumps(reqmsg)
conn.request("POST","", sxyz)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

if OCR_FLAG:
    reqmsg = messages.ocr_req_self
    reqmsg['sender']['userID'] = uid1
    reqmsg['sender']['wizUserID'] = wuid1
    reqmsg['sender']['wizCardID'] = e1_id
    print "OCR Req Own Card", reqmsg['sender']['userID']
    reqmsg['sender']['f_ocrCardImage'] = ocr_out
    ors = json.dumps(reqmsg)
    conn.request("POST","", ors)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])

    reqmsg = messages.ocr_dead_card
    reqmsg['sender']['userID'] = uid1
    reqmsg['sender']['wizUserID'] = wuid1
    reqmsg['sender']['wizCardID'] = e1_id
    print "Dead Card OCR ", reqmsg['sender']['userID']
    reqmsg['sender']['f_ocrCardImage'] = ocr_out
    ordc = json.dumps(reqmsg)
    conn.request("POST","", ordc)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])
    dc1_id = objs['data']['response']['id']

    reqmsg = messages.ocr_dead_card_edit
    reqmsg['sender']['userID'] = uid1
    reqmsg['sender']['wizUserID'] = wuid1
    reqmsg['sender']['deadCardID'] = dc1_id
    print "Dead Card Edit ", reqmsg['sender']['userID']
    dc1 = json.dumps(reqmsg)
    conn.request("POST","", dc1)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])


####wizweb messages########################
#query user
print "wizweb query existing user"
reqmsg = messages.wizweb_query_user
#reqmsg['sender']['username'] = USERNAME1
wwqu1 = json.dumps(reqmsg)
print wwqu1
conn.request("POST","", wwqu1)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])


print "wizweb query non-existing user"
reqmsg['sender']['username'] = "does not exist"
print "wizweb message query_user ", reqmsg['sender']['username']
wwqu2 = json.dumps(reqmsg)
print wwqu2
conn.request("POST","", wwqu2)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])


#query wizcard
print "wizweb query existing wizcard"
reqmsg = messages.wizweb_query_wizcard
#reqmsg['sender']['username'] = USERNAME1
reqmsg['sender']['userID'] = uid1
print "wizweb message query_wizcard ", reqmsg['sender']['username']
wwqwc1 = json.dumps(reqmsg)
print wwqwc1
conn.request("POST","", wwqwc1)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

print "wizweb query non-valid wizcard"
reqmsg['sender']['username'] = USERNAME1
reqmsg['sender']['userID'] = uid2
print "wizweb message query invalid wizcard ", reqmsg['sender']['userID']
wwqwc2 = json.dumps(reqmsg)
print wwqwc2
conn.request("POST","", wwqwc2)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

#wizweb user create
print "wizweb user create"
reqmsg = messages.wizweb_create_user
reqmsg['sender']['username'] = USERNAME4
reqmsg['sender']['first_name'] = USERNAME4_FIRST_NAME
reqmsg['sender']['last_name'] = USERNAME4_LAST_NAME
print "wizweb message user create ", reqmsg['sender']['username']
wwcu4 = json.dumps(reqmsg)
print wwcu4
conn.request("POST","", wwcu4)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
uid4 = objs['data']['userID']

#wizweb add card new
print "wizweb add card latest"
reqmsg = messages.wizweb_add_edit_card
reqmsg['sender']['username'] = USERNAME4
reqmsg['sender']['userID'] = uid4
reqmsg['sender']['mode'] = 1
reqmsg['sender']['first_name'] = USERNAME4_FIRST_NAME
reqmsg['sender']['last_name'] = USERNAME4_LAST_NAME
reqmsg['sender']['phone'] = PHONE4
reqmsg['sender']['title'] = DEFAULT_TITLE
reqmsg['sender']['company'] = DEFAULT_COMPANY
reqmsg['sender']['start'] = START1
reqmsg['sender']['mediaUrl'] = DEFAULT_MEDIA_URL
reqmsg['sender']['f_bizCardUrl'] = DEFAULT_BIZCARD_URL
print "wizweb message edit card latest ", reqmsg['sender']['userID']
wwaewc1 = json.dumps(reqmsg)
print wwaewc1
conn.request("POST","", wwaewc1)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

#wizweb edit card
print "wizweb edit card force"
reqmsg = messages.wizweb_add_edit_card
reqmsg['sender']['username'] = USERNAME1
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['mode'] = 2
reqmsg['sender']['first_name'] = USERNAME1
reqmsg['sender']['last_name'] = USERNAME1
reqmsg['sender']['phone'] = PHONE1
reqmsg['sender']['title'] = DEFAULT_TITLE
reqmsg['sender']['company'] = DEFAULT_COMPANY
reqmsg['sender']['start'] = START1
reqmsg['sender']['mediaUrl'] = DEFAULT_MEDIA_URL
reqmsg['sender']['f_bizCardUrl'] = DEFAULT_BIZCARD_URL
print "wizweb message edit card force ", reqmsg['sender']['userID']
wwaewc2 = json.dumps(reqmsg)
print wwaewc2
conn.request("POST","", wwaewc2)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.get_cards
reqmsg['sender']['userID'] = uid2
reqmsg['sender']['wizUserID'] = wuid2
print "GET cards", reqmsg['sender']['userID']
gcu2 = json.dumps(reqmsg)
conn.request("POST","", gcu2)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

notif = NotifParser(objs['data'], uid2, wuid2)
nrsp = notif.process_one()
while nrsp != False:
    if nrsp is not None:
        nrsp = json.dumps(nrsp)
        conn.request("POST","", n)
        # Parse and dump the JSON response from server
        objs = handle_response(conn, reqmsg['header']['msgType'])
    nrsp = notif.process_one()

reqmsg = messages.get_cards
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
print "GET cards", reqmsg['sender']['userID']
gcu3 = json.dumps(reqmsg)
conn.request("POST","", gcu3)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

notif = NotifParser(objs['data'], uid3, wuid3)
nrsp = notif.process_one()
while nrsp != False:
    if nrsp is not None:
        nrsp = json.dumps(nrsp)
        conn.request("POST","", n)
        # Parse and dump the JSON response from server
        objs = handle_response(conn, reqmsg['header']['msgType'])
    nrsp = notif.process_one()


reqmsg = messages.meishi_start
reqmsg['sender']['userID'] = uid2
reqmsg['sender']['wizUserID'] = wuid2
reqmsg['sender']['wizCardID'] = e1_id
reqmsg['sender']['lat'] = LAT1
reqmsg['sender']['lng'] = LNG1
print "MEISHI START", reqmsg['sender']['wizCardID']
mei2 = json.dumps(reqmsg)
print "sending meishi_start" + mei2
conn.request("POST", "", mei2)
objs = handle_response(conn,reqmsg['header']['msgType'])
mei_id2 = objs['data']['mID']
m_nearby = objs['data']['m_nearby']

reqmsg = messages.meishi_find
reqmsg['sender']['userID'] = uid2
reqmsg['sender']['wizUserID'] = wuid2
reqmsg['sender']['mID'] = mei_id2
print "MEISHI FIND", reqmsg['sender']['wizCardID']
mef2 = json.dumps(reqmsg)
print "sending meishi_find" + mef2
conn.request("POST", "", mef2)
objs = handle_response(conn,reqmsg['header']['msgType'])
if objs['data'].has_key('m_result'):
    mei_pair = objs['data']['m_result']
else:
    #expect nearby response
    m_nearby = objs['data']['m_nearby']

reqmsg = messages.meishi_start
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
reqmsg['sender']['wizCardID'] = e3_id
reqmsg['sender']['lat'] = LAT1
reqmsg['sender']['lng'] = LNG1
print "MEISHI START", reqmsg['sender']['wizCardID']
mei3 = json.dumps(reqmsg)
print "sending meishi_start" + mei3
conn.request("POST", "", mei3)
objs = handle_response(conn,reqmsg['header']['msgType'])
mei_id3 = objs['data']['mID']

print "Meishi ID = " + str(mei_id3)

reqmsg = messages.meishi_find
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
reqmsg['sender']['mID'] = mei_id3
print "MEISHI FIND", reqmsg['sender']['wizCardID']
mef3 = json.dumps(reqmsg)
print "sending meishi_find" + mef3
conn.request("POST", "", mef3)
objs = handle_response(conn,reqmsg['header']['msgType'])
mei_pair = objs['data']['m_result']

print "Meishi ID = " + str(mei_pair)
