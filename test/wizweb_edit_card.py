#!/usr/bin/python

# Test WizCard client (the real one resides on a smartphone - iphone, android)

# Standard imports
import httplib
import json
import pdb
import messages
from notifications import NotifParser
import random
import string

#1 Flick
#2 flick
#3 flick

#1 - 3 Connected


#T1 - [u1, u2] 

#1 - 2 Connected

#T2 - [u2]
#T3 - [u3]

PHONE = ""
USERNAME = ""
USERNAME_FIRST_NAME = "WizWeb_1"
USERNAME_LAST_NAME = "Last_1"

DEVICE_ID1 = "aaaaaaaaaaaaaaaaaaaaaaaaaa"
DEVICE_ID2 = "bbbbbbbbbbbbbbbbbbbbbbbbbb"
DEVICE_ID3 = "cccccccccccccccccccccccccc"


HASH1 = "aaaaaaaaaaaaaaaaaaaaaaaaaa"
HASH2 = "bbbbbbbbbbbbbbbbbbbbbbbbbb"
HASH3 = "cccccccccccccccccccccccccc"

RESPONSE_KEY1 = "1234"
RESPONSE_KEY2 = "1234"
RESPONSE_KEY3 = "1234"

DEFAULT_TITLE = "CEO"
DEFAULT_COMPANY = "WizCard Inc"
START1 = "Jan 27, 2010"
DEFAULT_MEDIA_URL = "www.youtube.com"
DEFAULT_BIZCARD_URL = "www.youtube.com"

server_url = "www.totastyle.com"
#server_url = "localhost"
#server_url = "ec2-54-219-163-35.us-west-1.compute.amazonaws.com"

server_port = 8000
#server_port = 80

test_image_path = "/Users/aammundi/Pictures/iChat Icons/Flags/Russia.png"
# Open the connection to Wiz server
conn = httplib.HTTPConnection(server_url, server_port)


def handle_response(conn, msg_type):
    res = conn.getresponse()
    print res.status, res.reason
    objs = res.read()    
    objs = json.loads( objs )
    print "received respone for Message: ", msg_type
    print json.dumps(objs, sort_keys = True, indent = 2)
    return objs

#wizweb add card new
print "wizweb add card latest"
reqmsg = messages.wizweb_add_edit_card
reqmsg['sender']['username'] = USERNAME
reqmsg['sender']['userID'] = uid
reqmsg['sender']['mode'] = 1
reqmsg['sender']['first_name'] = USERNAME_FIRST_NAME
reqmsg['sender']['last_name'] = USERNAME_LAST_NAME
reqmsg['sender']['phone'] = PHONE4
reqmsg['sender']['title'] = DEFAULT_TITLE
reqmsg['sender']['company'] = DEFAULT_COMPANY
reqmsg['sender']['start'] = START1
reqmsg['sender']['mediaUrl'] = DEFAULT_MEDIA_URL
reqmsg['sender']['f_bizCardUrl'] = DEFAULT_BIZCARD_URL
print "wizweb message edit card latest ", reqmsg['sender']['userID']
wwaewc1 = json.dumps(reqmsg)
print wwaewc1
conn.request("POST","", wwaewc1)
# Parse and dump the JSON response from server
objs = handle_response(conn, reqmsg['header']['msgType'])
