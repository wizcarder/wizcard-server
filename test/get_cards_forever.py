#!/usr/bin/python

# Test WizCard client (the real one resides on a smartphone - iphone, android)

# Standard imports
import httplib
import json
import pdb
import messages
import sys
import time

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
while True:
    s_uid = sys.argv[1]
    s_wuid = sys.argv[2]
    get_cards_msg = messages.get_cards_u
    get_cards_msg['sender']['userID'] = s_uid
    get_cards_msg['sender']['wizUserID'] = s_wuid
    gcu1 = json.dumps(get_cards_msg)
    conn.request("POST","", gcu1)
    # Parse and dump the JSON response from server
    objs = handle_response(conn)

    time.sleep(1)
