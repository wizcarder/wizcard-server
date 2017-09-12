#!/usr/bin/python

# Test WizCard client (the real one resides on a smartphone - iphone, android)

# Standard imports
import httplib
import messages
import pdb
import sys
proj_path="."
sys.path.append(proj_path)
from libtest import send_request, handle_response, APP_VERSION

server_url = "testbe.getwizcard.com"

server_port = 80

# Open the connection to Wiz server
conn = httplib.HTTPConnection(server_url, server_port)

reqmsg = messages.get_events
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = 'ARCT26'
reqmsg['sender']['wizUserID'] = 557
#reqmsg['sender']['lat'] = messages.LAT1
#reqmsg['sender']['lng'] = messages.LNG1
reqmsg['sender']['lat'] = 30.702059
reqmsg['sender']['lng'] = 76.705626
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
'''

reqmsg = messages.entity_details
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = 'U7VDB5'
reqmsg['sender']['wizUserID'] =521 
reqmsg['sender']['entity_id'] =3 
reqmsg['sender']['entity_type'] ='EVT' 
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
'''