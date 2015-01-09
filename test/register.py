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
import utils

#1 Flick
#2 flick
#3 flick

#1 - 3 Connected


#T1 - [u1, u2] 

#1 - 2 Connected

#T2 - [u2]
#T3 - [u3]

TEST_IMAGE=False
OCR_FLAG = True

NEXMO_PHONE1 = "14084641727"
PHONE1 = "+14084641727"
PHONE2 = "+15085332708"
PHONE3 = "+15086892263"
PHONE4 = "+14086892263"

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

ContactList = [PHONE1, PHONE2, PHONE3]

server_url = "www.totastyle.com"
#server_url = "localhost"
#server_url = "ec2-54-219-163-35.us-west-1.compute.amazonaws.com"

server_port = 8000
#server_port = 80

test_image_path = "/Users/aammundi/Pictures/iChat Icons/Flags/Russia.png"
# Open the connection to Wiz server
conn = httplib.HTTPConnection(server_url, server_port)


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
test_image_path = "/Users/aammundi/Pictures/iChat Icons/Flags/Russia.png"
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

#send edit_cards for each
if TEST_IMAGE:
    f = open(test_image_path, 'rb')
    out = f.read().encode('hex')
else:
    out = None

reqmsg = messages.edit_card1
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
contacts = reqmsg['sender']['contact_container']
#populate file
for c in contacts:
    c['f_bizCardImage'] = out
    c['b_bizCardImage'] = out
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
    c['f_bizCardImage'] = out
    c['b_bizCardImage'] = out
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
    c['f_bizCardImage'] = out
    c['b_bizCardImage'] = out
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
reqmsg['receiver']['verify_list'] = ContactList
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
tbl_c_3 = json.dumps(reqmsg)
conn.request("POST","", tbl_c_3)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
tid_3 = objs['data']['tableID']

#table query
reqmsg = messages.table_query
reqmsg['sender']['userID'] = uid3
reqmsg['sender']['wizUserID'] = wuid3
reqmsg['receiver']['name'] = TABLENAME_Q
tq3 = json.dumps(reqmsg)
conn.request("POST","", tq3)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])

#delete rolodex card
print "deleting all cards of ", uid3
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

reqmsg = messages.ocr_req_self
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['sender']['wizCardID'] = e1_id
print "OCR Req Own Card", reqmsg['sender']['userID']
ors = json.dumps(reqmsg)
if OCR_FLAG:
    conn.request("POST","", ors)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])

reqmsg = messages.ocr_dead_card
reqmsg['sender']['userID'] = uid1
reqmsg['sender']['wizUserID'] = wuid1
reqmsg['sender']['wizCardID'] = e1_id
print "Dead Card OCR ", reqmsg['sender']['userID']
ordc = json.dumps(reqmsg)
if OCR_FLAG:
    conn.request("POST","", ordc)
    # Parse and dump the JSON response from server
    objs = handle_response(conn, reqmsg['header']['msgType'])


####wizweb messages########################
#query user
print "wizweb query existing user"
reqmsg = messages.wizweb_query_user
reqmsg['sender']['username'] = USERNAME1
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
reqmsg['sender']['username'] = USERNAME1
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
