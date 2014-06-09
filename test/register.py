#!/usr/bin/python

# Test WizCard client (the real one resides on a smartphone - iphone, android)

# Standard imports
import httplib
import json
import pdb
import messages
from notifications import NotifParser

TEST_IMAGE=False

PHONE1 = "+15084641727"
PHONE2 = "+15085332708"
PHONE3 = "+15086892263"

USERNAME1 = PHONE1+'@wizcard.com'
USERNAME2 = PHONE2+'@wizcard.com'
USERNAME3 = PHONE3+'@wizcard.com'

DEVICE_ID1 = "aaaaaaaaaaaaaaaaaaaaaaaaaa"
DEVICE_ID2 = "bbbbbbbbbbbbbbbbbbbbbbbbbb"
DEVICE_ID3 = "cccccccccccccccccccccccccc"


HASH1 = "aaaaaaaaaaaaaaaaaaaaaaaaaa"
HASH2 = "bbbbbbbbbbbbbbbbbbbbbbbbbb"
HASH3 = "cccccccccccccccccccccccccc"

RESPONSE_KEY1 = "1234"
RESPONSE_KEY2 = "1234"
RESPONSE_KEY3 = "1234"

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


def handle_response(connection):
    res = conn.getresponse()
    print res.status, res.reason
    objs = res.read()    
    objs = json.loads( objs )
    print json.dumps(objs, sort_keys = True, indent = 2)
    return objs

pcreqmsg = messages.phone_check_req
pcreqmsg['header']['deviceID'] = DEVICE_ID1
pcreqmsg['header']['hash'] = HASH1
pcreqmsg['sender']['username'] = USERNAME1
pcreqmsg['sender']['target'] = PHONE1
pcreqmsg['sender']['responseMode'] = 'sms'
pcreq1 = json.dumps(pcreqmsg)
conn.request("POST","", pcreq1)
print "sending phone_check_req", pcreq1
# Parse and dump the JSON response from server
objs = handle_response(conn)

pcrspmsg = messages.phone_check_resp
pcrspmsg['header']['deviceID'] = DEVICE_ID1
pcrspmsg['header']['hash'] = HASH1
pcrspmsg['sender']['username'] = USERNAME1
pcrspmsg['sender']['responseKey'] = RESPONSE_KEY1
pcrsp1 = json.dumps(pcrspmsg)
print "sending phone_check_rsp", pcrsp1
conn.request("POST","", pcrsp1)
# Parse and dump the JSON response from server
objs = handle_response(conn)
uid1 = objs['data']['userID']

pcreqmsg = messages.phone_check_req
pcreqmsg['header']['deviceID'] = DEVICE_ID2
pcreqmsg['header']['hash'] = HASH2
pcreqmsg['sender']['username'] = USERNAME2
pcreqmsg['sender']['target'] = PHONE2
pcreqmsg['sender']['responseMode'] = 'sms'
pcreq2 = json.dumps(pcreqmsg)
conn.request("POST","", pcreq2)
print "sending phone_check_req", pcreq2
# Parse and dump the JSON response from server
objs = handle_response(conn)

pcrspmsg = messages.phone_check_resp
pcrspmsg['header']['deviceID'] = DEVICE_ID2
pcrspmsg['header']['hash'] = HASH2
pcrspmsg['sender']['username'] = USERNAME2
pcrspmsg['sender']['responseKey'] = RESPONSE_KEY2
pcrsp2 = json.dumps(pcrspmsg)
print "sending phone_check_rsp", pcrsp2
conn.request("POST","", pcrsp2)
# Parse and dump the JSON response from server
objs = handle_response(conn)
uid2 = objs['data']['userID']

pcreqmsg = messages.phone_check_req
pcreqmsg['header']['deviceID'] = DEVICE_ID3
pcreqmsg['header']['hash'] = HASH3
pcreqmsg['sender']['username'] = USERNAME3
pcreqmsg['sender']['target'] = PHONE3
pcreqmsg['sender']['responseMode'] = 'sms'
pcreq3 = json.dumps(pcreqmsg)
conn.request("POST","", pcreq3)
print "sending phone_check_req", pcreq3
# Parse and dump the JSON response from server
objs = handle_response(conn)

#resp = objs['data']['key']
pcrspmsg = messages.phone_check_resp
pcrspmsg['header']['deviceID'] = DEVICE_ID3
pcrspmsg['header']['hash'] = HASH3
pcrspmsg['sender']['username'] = USERNAME3
pcrspmsg['sender']['responseKey'] = RESPONSE_KEY3
pcrsp3 = json.dumps(pcrspmsg)
test_image_path = "/Users/aammundi/Pictures/iChat Icons/Flags/Russia.png"
print "sending phone_check_rsp", pcrsp3
conn.request("POST","", pcrsp3)
# Parse and dump the JSON response from server
objs = handle_response(conn)
uid3 = objs['data']['userID']

lmsg = messages.login
lmsg['sender']['username'] = USERNAME1
lmsg['sender']['userID'] = uid1
login = json.dumps(lmsg)
print "sending login", login
conn.request("POST","", login)
# Parse and dump the JSON response from server
objs = handle_response(conn)
wuid1 = objs['data']['wizUserID']

lmsg['sender']['username'] = USERNAME2
lmsg['sender']['userID'] = uid2
login = json.dumps(lmsg)
print "sending login", login
conn.request("POST","", login)
# Parse and dump the JSON response from server
objs = handle_response(conn)
wuid2 = objs['data']['wizUserID']

lmsg['sender']['username'] = USERNAME3
lmsg['sender']['userID'] = uid3
login = json.dumps(lmsg)
print "sending login", login
conn.request("POST","", login)
# Parse and dump the JSON response from server
objs = handle_response(conn)
wuid3 = objs['data']['wizUserID']

#send register

#create 3 users
rmsg = messages.register1
rmsg['sender']['userID']=uid1
rmsg['sender']['wizUserID']=wuid1
r1 = json.dumps(rmsg)
conn.request("POST","", r1)
print "sending register"
# Parse and dump the JSON response from server
objs = handle_response(conn)

rmsg = messages.register2
rmsg['sender']['userID']=uid2
rmsg['sender']['wizUserID']=wuid2
r2 = json.dumps(rmsg)
conn.request("POST","", r2)
# Parse and dump the JSON response from server
print "sending register"
objs = handle_response(conn)

rmsg = messages.register3
rmsg['sender']['userID']=uid3
rmsg['sender']['wizUserID']=wuid3
r3 = json.dumps(rmsg)
conn.request("POST","", r3)
print "sending register"
# Parse and dump the JSON response from server
objs = handle_response(conn)

#send edit_cards for each
if TEST_IMAGE:
    f = open(test_image_path, 'rb')
    out = f.read().encode('hex')
else:
    out = None

edit_card_msg = messages.edit_card1
edit_card_msg['sender']['userID'] = uid1
edit_card_msg['sender']['wizUserID'] = wuid1
contacts = edit_card_msg['sender']['contact_container']
#populate file
for c in contacts:
    c['f_bizCardImage'] = out
    c['b_bizCardImage'] = out
e1 = json.dumps(edit_card_msg)
print "sending EDIT CARD for", edit_card_msg['sender']['userID']
conn.request("POST","", e1)
# Parse and dump the JSON response from server
objs = handle_response(conn)
e1_id = objs['data']['wizCardID']


edit_card_msg = messages.edit_card2
edit_card_msg['sender']['userID'] = uid2
edit_card_msg['sender']['wizUserID'] = wuid2
contacts = edit_card_msg['sender']['contact_container']
#populate file
for c in contacts:
    c['f_bizCardImage'] = out
    c['b_bizCardImage'] = out
e2 = json.dumps(edit_card_msg)
print "sending EDIT CARD for", edit_card_msg['sender']['userID']
conn.request("POST","", e2)
# Parse and dump the JSON response from server
objs = handle_response(conn)
e2_id = objs['data']['wizCardID']

edit_card_msg = messages.edit_card3
edit_card_msg['sender']['userID'] = uid3
edit_card_msg['sender']['wizUserID'] = wuid3
contacts = edit_card_msg['sender']['contact_container']
#populate file
for c in contacts:
    c['f_bizCardImage'] = out
    c['b_bizCardImage'] = out
e3 = json.dumps(edit_card_msg)
print "sending EDIT CARD for", edit_card_msg['sender']['userID']
conn.request("POST","", e3)
# Parse and dump the JSON response from server
objs = handle_response(conn)
e3_id = objs['data']['wizCardID']

#send location update
location_msg = messages.location
location_msg['sender']['lat'] = LAT1
location_msg['sender']['lng'] = LNG1
location_msg['sender']['userID'] = uid1
location_msg['sender']['wizUserID'] = wuid1
l1 = json.dumps(location_msg)
print "sending Location Update for", location_msg['sender']['userID']
conn.request("POST","", l1)
# Parse and dump the JSON response from server
objs = handle_response(conn)

#contacts verify
contacts_verify_msg = messages.contacts_verify
contacts_verify_msg['sender']['userID'] = uid1
contacts_verify_msg['sender']['wizUserID'] = wuid1
contacts_verify_msg['receiver']['verify_list'] = ContactList
cv = json.dumps(contacts_verify_msg)
print "sending Contact Verify", contacts_verify_msg['sender']['userID']
conn.request("POST","", cv)
# Parse and dump the JSON response from server
objs = handle_response(conn)

card_flick_msg = messages.card_flick
card_flick_msg['sender']['userID'] = uid1
card_flick_msg['sender']['wizUserID'] = wuid1
print "flicking card", card_flick_msg['sender']['userID']
cf1 = json.dumps(card_flick_msg)
conn.request("POST","", cf1)
# Parse and dump the JSON response from server
objs = handle_response(conn)
cf1_id = objs['data']['flickCardID']

#re flick to check agglomeration
card_flick_msg = messages.card_flick
card_flick_msg['sender']['userID'] = uid1
card_flick_msg['sender']['wizUserID'] = wuid1
print "re-flicking card from same location", card_flick_msg['sender']['userID']
cf1 = json.dumps(card_flick_msg)
conn.request("POST","", cf1)
# Parse and dump the JSON response from server
objs = handle_response(conn)
cf1_id = objs['data']['flickCardID']

#re flick to check agglomeration
card_flick_msg = messages.card_flick
card_flick_msg['sender']['userID'] = uid1
card_flick_msg['sender']['wizUserID'] = wuid1
print "re-flicking card from close-by location", card_flick_msg['sender']['userID']
card_flick_msg['sender']['lng'] += 0.000001
cf2 = json.dumps(card_flick_msg)
conn.request("POST","", cf2)
# Parse and dump the JSON response from server
objs = handle_response(conn)
cf2_id = objs['data']['flickCardID']

card_flick_msg = messages.card_flick
card_flick_msg['sender']['userID'] = uid3
card_flick_msg['sender']['wizUserID'] = wuid3
print "flicking card", card_flick_msg['sender']['userID']
cf3 = json.dumps(card_flick_msg)
conn.request("POST","", cf3)
# Parse and dump the JSON response from server
objs = handle_response(conn)
cf3_id = objs['data']['flickCardID']

print "pick up flicked card"
card_flick_accept_msg = messages.card_flick_accept
card_flick_accept_msg['sender']['userID'] = uid1
card_flick_accept_msg['sender']['wizUserID'] = wuid1
card_flick_accept_msg['receiver']['flickCardIDs'] = [cf3_id]
cfa1 = json.dumps(card_flick_accept_msg)
conn.request("POST","", cfa1)
# Parse and dump the JSON response from server
objs = handle_response(conn)

print "retrieving myFlicks"
my_flick_msg = messages.my_flicks
my_flick_msg['sender']['userID'] = uid1
my_flick_msg['sender']['wizUserID'] = wuid1
my_flick_msg['sender']['wizCardID'] = e1_id
mcf1 = json.dumps(my_flick_msg)
conn.request("POST","", mcf1)
# Parse and dump the JSON response from server
objs = handle_response(conn)

my_flick_msg = messages.my_flicks
my_flick_msg['sender']['userID'] = uid3
my_flick_msg['sender']['wizUserID'] = wuid3
my_flick_msg['sender']['wizCardID'] = e3_id
mcf3 = json.dumps(my_flick_msg)
conn.request("POST","", mcf3)
# Parse and dump the JSON response from server
objs = handle_response(conn)

print "Creating Table"
tbl_create_msg = messages.table_create
tbl_create_msg['sender']['userID'] = uid1
tbl_create_msg['sender']['wizUserID'] = wuid1
tbl_create_msg['sender']['table_name'] = "One"
tbl_c_1 = json.dumps(tbl_create_msg)
conn.request("POST","", tbl_c_1)
# Parse and dump the JSON response from server
objs = handle_response(conn)
tid_1 = objs['data']['tableID']

#join created table
print "Joining Table"
tbl_join_msg = messages.table_join
tbl_join_msg['sender']['userID'] = uid2
tbl_join_msg['sender']['wizUserID'] = wuid2
tbl_join_msg['sender']['tableID'] = tid_1
tbl_j_1 = json.dumps(tbl_join_msg)
conn.request("POST","", tbl_j_1)
# Parse and dump the JSON response from server
objs = handle_response(conn)

print "Joining Table with error password"
tbl_join_msg = messages.table_join
tbl_join_msg['sender']['userID'] = uid3
tbl_join_msg['sender']['wizUserID'] = wuid3
tbl_join_msg['sender']['tableID'] = tid_1
tbl_join_msg['sender']['password'] = "xxx"
tbl_j_1 = json.dumps(tbl_join_msg)
# Parse and dump the JSON response from server
conn.request("POST","", tbl_j_1)
objs = handle_response(conn)

print "get cards for user", uid1
get_cards_msg = messages.get_cards
get_cards_msg['sender']['userID'] = uid1
get_cards_msg['sender']['wizUserID'] = wuid1
print "GET cards", get_cards_msg['sender']['userID']
gcu1 = json.dumps(get_cards_msg)
conn.request("POST","", gcu1)
# Parse and dump the JSON response from server
objs = handle_response(conn)

notif = NotifParser(objs['data'], uid1, wuid1)
nrsp = notif.process_one()
while nrsp != False:
    if nrsp is not None:
        nrsp = json.dumps(nrsp)
        conn.request("POST","", n)
        # Parse and dump the JSON response from server
        objs = handle_response(conn)
    nrsp = notif.process_one()

get_cards_msg = messages.get_cards
get_cards_msg['sender']['userID'] = uid2
get_cards_msg['sender']['wizUserID'] = wuid2
print "GET cards", get_cards_msg['sender']['userID']
gcu2 = json.dumps(get_cards_msg)
conn.request("POST","", gcu2)
# Parse and dump the JSON response from server
objs = handle_response(conn)

notif = NotifParser(objs['data'], uid2, wuid2)
nrsp = notif.process_one()
while nrsp != False:
    if nrsp is not None:
        nrsp = json.dumps(nrsp)
        conn.request("POST","", n)
        # Parse and dump the JSON response from server
        objs = handle_response(conn)
    nrsp = notif.process_one()

get_cards_msg = messages.get_cards
get_cards_msg['sender']['userID'] = uid3
get_cards_msg['sender']['wizUserID'] = wuid3
print "GET cards", get_cards_msg['sender']['userID']
gcu3 = json.dumps(get_cards_msg)
conn.request("POST","", gcu3)
# Parse and dump the JSON response from server
objs = handle_response(conn)

notif = NotifParser(objs['data'], uid3, wuid3)
nrsp = notif.process_one()
while nrsp != False:
    if nrsp is not None:
        nrsp = json.dumps(nrsp)
        conn.request("POST","", n)
        # Parse and dump the JSON response from server
        objs = handle_response(conn)
    nrsp = notif.process_one()

card_details_msg = messages.card_details
card_details_msg['sender']['userID'] = uid1
card_details_msg['sender']['wizUserID'] = wuid1
card_details_msg['receiver']['wizCardID'] = e1_id
print "GET card DETAILS", card_details_msg['sender']['userID']
cd1 = json.dumps(card_details_msg)
conn.request("POST","", cd1)
# Parse and dump the JSON response from server
objs = handle_response(conn)

card_details_msg = messages.card_details
card_details_msg['sender']['userID'] = uid2
card_details_msg['sender']['wizUserID'] = wuid2
card_details_msg['receiver']['wizCardID'] = e2_id
print "GET card DETAILS", card_details_msg['sender']['userID']
cd2 = json.dumps(card_details_msg)
conn.request("POST","", cd2)
# Parse and dump the JSON response from server
objs = handle_response(conn)

card_details_msg = messages.card_details
card_details_msg['sender']['userID'] = uid3
card_details_msg['sender']['wizUserID'] = wuid3
card_details_msg['receiver']['wizCardID'] = e3_id
print "GET card DETAILS", card_details_msg['sender']['userID']
cd3 = json.dumps(card_details_msg)
conn.request("POST","", cd3)
# Parse and dump the JSON response from server
objs = handle_response(conn)
