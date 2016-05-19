#!/usr/bin/python

# Test WizCard client (the real one resides on a smartphone - iphone, android)

# Standard imports
import httplib
import json
import pdb
import messages

server_url = "ec2-52-8-161-151.us-west-1.compute.amazonaws.com"

server_port = 80
USERID = "SP9HAR"
WIZUSERID = 2

# Open the connection to Wiz server
conn = httplib.HTTPConnection(server_url, server_port)

def handle_response(connection):
    res = conn.getresponse()
    print res.status, res.reason
    objs = res.read()
    objs = json.loads( objs )
    print json.dumps(objs, sort_keys = True, indent = 2)
    return objs

get_cards_u1_msg = messages.get_cards
get_cards_u1_msg['sender']['userID'] = USERID
get_cards_u1_msg['sender']['wizUserID'] = WIZUSERID
gcu1 = json.dumps(get_cards_u1_msg)
conn.request("POST","", gcu1)
# Parse and dump the JSON response from server
objs = handle_response(conn)
