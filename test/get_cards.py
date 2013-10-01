#!/usr/bin/python

# Test WizCard client (the real one resides on a smartphone - iphone, android)

# Standard imports
import httplib
import json
import pdb
import messages

server_url = "www.totastyle.com"
#server_url = "localhost"

server_port = 8000

# Open the connection to Wiz server
conn = httplib.HTTPConnection(server_url, server_port)

def handle_response(connection):
    res = conn.getresponse()
    print res.status, res.reason
    objs = res.read()    
    objs = json.loads( objs )
    print json.dumps(objs, sort_keys = True, indent = 2)
    return objs

get_cards_u3_msg = messages.get_cards_u3
get_cards_u3_msg['sender']['userID'] = "USER3"
get_cards_u3_msg['sender']['wizUserID'] = 3
gcu3 = json.dumps(get_cards_u3_msg)
conn.request("POST","", gcu3)
# Parse and dump the JSON response from server
objs = handle_response(conn)
