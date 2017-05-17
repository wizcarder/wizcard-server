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

server_url = "localhost"

server_port = 8000

# Open the connection to Wiz server
conn = httplib.HTTPConnection(server_url, server_port)


reqmsg = messages.get_events
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['userID'] = 'MO3HR8'
reqmsg['sender']['wizUserID'] = 3
reqmsg['sender']['lat'] = messages.LAT1
reqmsg['sender']['lng'] = messages.LNG1
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
