#!/usr/bin/python

# Test WizCard client (the real one resides on a smartphone - iphone, android)

# Standard imports
import httplib
import json
import pdb
import messages

#server_url = "www.totastyle.com"
#server_url = "localhost"
server_url = "ec2-54-219-163-35.us-west-1.compute.amazonaws.com"

server_port = 8000
#server_port = 80

# Open the connection to Wiz server
conn = httplib.HTTPConnection(server_url, server_port)

def handle_response(connection):
    res = conn.getresponse()
    print res.status, res.reason
    objs = res.read()    
    objs = json.loads( objs )
    print json.dumps(objs, sort_keys = True, indent = 2)
    return objs

#send register

#create 3 users
rmsg = messages.register1
r1 = json.dumps(rmsg)
conn.request("POST","", r1)
print "creating USER", rmsg['sender']['userID']
# Parse and dump the JSON response from server
objs = handle_response(conn)
r1_id = objs['data']['wizUserID']

rmsg = messages.register2
r2 = json.dumps(rmsg)
conn.request("POST","", r2)
# Parse and dump the JSON response from server
print "creating USER", rmsg['sender']['userID']
objs = handle_response(conn)
r2_id = objs['data']['wizUserID']

rmsg = messages.register3
r3 = json.dumps(rmsg)
conn.request("POST","", r3)
print "creating USER", rmsg['sender']['userID']
# Parse and dump the JSON response from server
objs = handle_response(conn)
r3_id = objs['data']['wizUserID']

#send edit_cards for each
edit_card_msg = messages.edit_card1
edit_card_msg['sender']['wizUserID'] = r1_id
e1 = json.dumps(edit_card_msg)
print "sending EDIT CARD for", edit_card_msg['sender']['userID']
conn.request("POST","", e1)
# Parse and dump the JSON response from server
objs = handle_response(conn)
e1_id = objs['data']['wizCardID']


edit_card_msg = messages.edit_card2
edit_card_msg['sender']['wizUserID'] = r2_id
e2 = json.dumps(edit_card_msg)
print "sending EDIT CARD for", edit_card_msg['sender']['userID']
conn.request("POST","", e2)
# Parse and dump the JSON response from server
objs = handle_response(conn)
e2_id = objs['data']['wizCardID']

edit_card_msg = messages.edit_card3
edit_card_msg['sender']['wizUserID'] = r3_id
e3 = json.dumps(edit_card_msg)
print "sending EDIT CARD for", edit_card_msg['sender']['userID']
conn.request("POST","", e3)
# Parse and dump the JSON response from server
objs = handle_response(conn)
e3_id = objs['data']['wizCardID']

card_flick_msg = messages.card_flick
card_flick_msg['sender']['userID'] = "USER1"
card_flick_msg['sender']['wizUserID'] = r1_id
print "flicking card", card_flick_msg['sender']['userID']
cf1 = json.dumps(card_flick_msg)
conn.request("POST","", cf1)
# Parse and dump the JSON response from server
objs = handle_response(conn)

#re flick to check agglomeration
card_flick_msg = messages.card_flick
card_flick_msg['sender']['userID'] = "USER1"
card_flick_msg['sender']['wizUserID'] = r1_id
print "re-flicking card from same location", card_flick_msg['sender']['userID']
cf1 = json.dumps(card_flick_msg)
conn.request("POST","", cf1)
# Parse and dump the JSON response from server
objs = handle_response(conn)

#re flick to check agglomeration
card_flick_msg = messages.card_flick
card_flick_msg['sender']['userID'] = "USER1"
card_flick_msg['sender']['wizUserID'] = r1_id
print "re-flicking card from close-by location", card_flick_msg['sender']['userID']
card_flick_msg['sender']['lng'] += 0.000001
cf1 = json.dumps(card_flick_msg)
conn.request("POST","", cf1)
# Parse and dump the JSON response from server
objs = handle_response(conn)

card_flick_msg = messages.card_flick
card_flick_msg['sender']['userID'] = "USER3"
card_flick_msg['sender']['wizUserID'] = r3_id
print "flicking card", card_flick_msg['sender']['userID']
cf3 = json.dumps(card_flick_msg)
conn.request("POST","", cf3)
# Parse and dump the JSON response from server
objs = handle_response(conn)

get_cards_msg = messages.get_cards_u
get_cards_msg['sender']['userID'] = "USER1"
get_cards_msg['sender']['wizUserID'] = r1_id
print "GET cards", get_cards_msg['sender']['userID']
gcu1 = json.dumps(get_cards_msg)
conn.request("POST","", gcu1)
# Parse and dump the JSON response from server
objs = handle_response(conn)

get_cards_msg = messages.get_cards_u
get_cards_msg['sender']['userID'] = "USER3"
get_cards_msg['sender']['wizUserID'] = r3_id
print "GET cards", get_cards_msg['sender']['userID']
gcu3 = json.dumps(get_cards_msg)
conn.request("POST","", gcu3)
# Parse and dump the JSON response from server
objs = handle_response(conn)

tbl_create_1_msg = messages.table_create_1
tbl_create_1_msg['sender']['userID'] = "USER1"
tbl_create_1_msg['sender']['wizUserID'] = r1_id
tbl_create_1_msg['sender']['table_name'] = "One"
tbl_c_1 = json.dumps(tbl_create_1_msg)
conn.request("POST","", tbl_c_1)
# Parse and dump the JSON response from server
objs = handle_response(conn)












