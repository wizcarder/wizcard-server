#!/usr/bin/python

# Test WizCard client (the real one resides on a smartphone - iphone, android)

# Standard imports
import httplib
import json
import pdb
import messages

#server_url = "www.totastyle.com"
server_url = "localhost"

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


card_flick_msg = messages.card_flick
card_flick_msg['sender']['wizUserID'] = 3
cf3 = json.dumps(card_flick_msg)
conn.request("POST","", cf3)
# Parse and dump the JSON response from server
objs = handle_response(conn)
