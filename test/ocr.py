#!/usr/bin/python

# Test WizCard client (the real one resides on a smartphone - iphone, android)

# Standard imports
import httplib
import messages
import libtest
import pdb
from libtest import send_request, handle_response, APP_VERSION

server_url = "localhost"

server_port = 8000

# Open the connection to Wiz server
conn = httplib.HTTPConnection(server_url, server_port)


f = open(libtest.ocr_image_path, 'rb')
ocr_out = f.read().encode('base64')

reqmsg = messages.ocr_req_self
reqmsg['header']['version'] = APP_VERSION
reqmsg['sender']['user_id'] = '6595f5d1-b194-4649-9b32-e69e61052c12'
reqmsg['sender']['wizuser_id'] = 8
reqmsg['sender']['f_ocr_card_image'] = ocr_out
send_request(conn, reqmsg)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msg_type'])
contact_container = objs['data']['ocr_result']['contact_container']