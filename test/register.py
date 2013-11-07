#!/usr/bin/python

# Test WizCard client (the real one resides on a smartphone - iphone, android)

# Standard imports
import httplib
import json
import pdb
import messages

#server_url = "www.totastyle.com"
server_url = "localhost"
#server_url = "ec2-54-219-163-35.us-west-1.compute.amazonaws.com"

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
r1 = json.dumps(messages.register1)
conn.request("POST","", r1)
# Parse and dump the JSON response from server
objs = handle_response(conn)
r1_id = objs['data']['wizUserID']

r2 = json.dumps(messages.register2)
conn.request("POST","", r2)
# Parse and dump the JSON response from server
objs = handle_response(conn)
r2_id = objs['data']['wizUserID']

r3 = json.dumps(messages.register3)
conn.request("POST","", r3)
# Parse and dump the JSON response from server
objs = handle_response(conn)
r3_id = objs['data']['wizUserID']


#send edit_cards for each
edit_card_msg = messages.edit_card1
edit_card_msg['sender']['wizUserID'] = r1_id
e1 = json.dumps(edit_card_msg)
conn.request("POST","", e1)
# Parse and dump the JSON response from server
objs = handle_response(conn)
e1_id = objs['data']['wizCardID']


edit_card_msg = messages.edit_card2
edit_card_msg['sender']['wizUserID'] = r2_id
e2 = json.dumps(edit_card_msg)
conn.request("POST","", e2)
# Parse and dump the JSON response from server
objs = handle_response(conn)
e2_id = objs['data']['wizCardID']

edit_card_msg = messages.edit_card3
edit_card_msg['sender']['wizUserID'] = r3_id
e3 = json.dumps(edit_card_msg)
conn.request("POST","", e3)
# Parse and dump the JSON response from server
objs = handle_response(conn)
e3_id = objs['data']['wizCardID']

card_flick_msg = messages.card_flick
card_flick_msg['sender']['wizUserID'] = r3_id
cf3 = json.dumps(card_flick_msg)
conn.request("POST","", cf3)
# Parse and dump the JSON response from server
objs = handle_response(conn)

get_cards_u3_msg = messages.get_cards_u3
get_cards_u3_msg['sender']['userID'] = "USER3"
get_cards_u3_msg['sender']['wizUserID'] = r3_id
gcu3 = json.dumps(get_cards_u3_msg)
conn.request("POST","", gcu3)
# Parse and dump the JSON response from server
objs = handle_response(conn)







