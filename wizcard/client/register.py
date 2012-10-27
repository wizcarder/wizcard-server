#!/usr/bin/python

# Test WizCard client (the real one resides on a smartphone - iphone, android)

# Standard imports
import httplib
import json
import pdb

# Wiz specific imports

# Open the connection to Wiz server
conn = httplib.HTTPConnection("localhost", 8000)

#Send a test GET request
#conn.request("GET", "")
#res = conn.getresponse()
#print res.status, res.reason

# Dump the JSON object received in response
#objs = res.read()    
#objs = json.loads( objs )
#print objs

#register1 = {
#    "deviceID": "A000111",
#    "userID": "anand",
#    "firstname":"Anand",
#    "lastname":"Ammundi",
#    "email": "anand@oz.com",
#    "phone1":"408-464-1727",
#    "seqNum": "1000",
#    "msgType":"register",
#    "message": {"lat":37.32300, "lng":-122.03218}
#}
#
#register2 = {
#    "deviceID": "A000113",
#    "userID": "ishaan",
#    "firstname":"Ishaan",
#    "lastname":"Ammundi",
#    "email": "ishaan@oz.com",
#    "phone1":"408-464-1337",
#    "seqNum": "1000",
#    "msgType":"register",
#    "message": {"lat":37.32300, "lng":-122.03218}
#}

register3 = {
    "deviceID": "A000112",
    "userID": "ronak",
    "firstname":"Ronak",
    "lastname":"Shah",
    "email": "ronak@oz.com",
    "phone1":"408-484-1727",
    "seqNum": "1000",
    "msgType":"register",
    "message": {"lat":37.32300, "lng":-122.03218}
}

register4 = {
    "deviceID": "A000112",
    "userID": "mariya",
    "firstname":"Mariya",
    "lastname":"Kholod",
    "email": "mariya@oz.com",
    "phone1":"408-464-1727",
    "seqNum": "1000",
    "msgType":"register",
    "message": {"lat":37.32300, "lng":-122.03218}
}

register5 = {
    "deviceID": "A000112",
    "userID": "rudra",
    "firstname":"Rudra",
    "lastname":"Rugge",
    "email": "rudra@oz.com",
    "phone1":"408-434-1727",
    "seqNum": "1000",
    "msgType":"register",
    "message": {"lat":37.32300, "lng":-122.03218}
}

register6 = {
    "deviceID": "A000112",
    "userID": "pranay",
    "firstname":"Pranay",
    "lastname":"Pogde",
    "email": "pranay@oz.com",
    "phone1":"408-444-1727",
    "seqNum": "1000",
    "msgType":"register",
    "message": {"lat":37.32300, "lng":-122.03218}
}

#add_card1 = {
#    "deviceID" : "A00195EE-2A42-4E2F-9EFF-8FBD3475164B",
#    "message": {
#        "city" : "CityName",
#        "company" : "1",
#        "email" : "1@test.com",
#        "first" : "Anand",
#        "last" : "Ammundi",
#        "phone" : "123456789",
#        "state" : "StateName",
#        "street" : "StreetName",
#        "thumbnailImage" : "...",
#        "title" : "My position",
#        "zip" : "00000",
#    },
#    "msgType" : "add_card",
#    "seqNum" : "1000",
#    "userID" : "aammundi",
#}

#add_card2 = {
##    "deviceID" : "A00195EE-2A42-4E2F-9EFF-8FBD3475164B",
#    "message": {
#        "city" : "CityName",
#        "company" : "2",
#        "email" : "2@test.com",
#        "first" : "Ishaan",
#        "last" : "Ammundi",
#        "phone" : "123456789",
#        "state" : "StateName",
#        "street" : "StreetName",
#        "thumbnailImage" : "...",
#        "title" : "My position",
#        "zip" : "00000",
#    },
#    "msgType" : "add_card",
#    "seqNum" : "1000",
#    "userID" : "ishaan"
#}

add_card3 = {
    "deviceID" : "A00195EE-2A42-4E2F-9EFF-8FBD3475164B",
    "message": {
        "city" : "CityName",
        "company" : "3",
        "email" : "ronak@oz.com",
        "first" : "Ronak",
        "last" : "Shah",
        "phone" : "123456789",
        "state" : "StateName",
        "street" : "StreetName",
        "thumbnailImage" : "...",
        "title" : "My position",
        "zip" : "00000",
    },
    "msgType" : "add_card",
    "seqNum" : "1000",
    "userID" : "ronak"
}

add_card4 = {
    "deviceID" : "A00195EE-2A42-4E2F-9EFF-8FBD3475164B",
    "message": {
        "city" : "CityName",
        "company" : "4",
        "email" : "mariya@oz.com",
        "first" : "Mariya",
        "last" : "Kholod",
        "phone" : "123456789",
        "state" : "StateName",
        "street" : "StreetName",
        "thumbnailImage" : "...",
        "title" : "My position",
        "zip" : "00000",
    },
    "msgType" : "add_card",
    "seqNum" : "1000",
    "userID" : "mariya"
}

add_card5 = {
    "deviceID" : "A00195EE-2A42-4E2F-9EFF-8FBD3475164B",
    "message": {
        "city" : "CityName",
        "company" : "5",
        "email" : "rudra@oz.com",
        "first" : "Rudra",
        "last" : "Rugge",
        "phone" : "123456789",
        "state" : "StateName",
        "street" : "StreetName",
        "thumbnailImage" : "...",
        "title" : "My position",
        "zip" : "00000",
    },
    "msgType" : "add_card",
    "seqNum" : "1000",
    "userID" : "rudra"
}

add_card6 = {
    "deviceID" : "A00195EE-2A42-4E2F-9EFF-8FBD3475164B",
    "message": {
        "city" : "CityName",
        "company" : "6",
        "email" : "pranay@oz.com",
        "first" : "Pranay",
        "last" : "Pogde",
        "phone" : "123456789",
        "state" : "StateName",
        "street" : "StreetName",
        "thumbnailImage" : "...",
        "title" : "My position",
        "zip" : "00000",
    },
    "msgType" : "add_card",
    "seqNum" : "1000",
    "userID" : "pranay"
}

def handle_response(connection):
    res = conn.getresponse()
    print res.status, res.reason
    objs = res.read()    
    objs = json.loads( objs )
    print json.dumps(objs, sort_keys = True, indent = 2)
    return objs




    

#r1 = json.dumps(register1)
#r2 = json.dumps(register2)
r3 = json.dumps(register3)
r4 = json.dumps(register4)
r5 = json.dumps(register5)
r6 = json.dumps(register6)
#a1 = json.dumps(add_card1)
#a2 = json.dumps(add_card2)
a3 = json.dumps(add_card3)
a4 = json.dumps(add_card4)
a5 = json.dumps(add_card5)
a6 = json.dumps(add_card6)

#register
#conn.request("POST","", r1)
#Parse and dump the JSON response from server
#objs = handle_response(conn)
#r1_id = objs['data']['wizUserID']

#conn.request("POST","", r2)
# Parse and dump the JSON response from server
#objs = handle_response(conn)
#r2_id = objs['data']['wizUserID']

conn.request("POST","", r3)
# Parse and dump the JSON response from server
objs = handle_response(conn)
r3_id = objs['data']['wizUserID']

conn.request("POST","", r4)
# Parse and dump the JSON response from server
objs = handle_response(conn)
r4_id = objs['data']['wizUserID']

conn.request("POST","", r5)
# Parse and dump the JSON response from server
objs = handle_response(conn)
r5_id = objs['data']['wizUserID']

conn.request("POST","", r6)
# Parse and dump the JSON response from server
objs = handle_response(conn)
r6_id = objs['data']['wizUserID']

#add cards
#conn.request("POST","", a1)
# Parse and dump the JSON response from server
#objs = handle_response(conn)
#a1wc = objs['data']['wizCardID']

#conn.request("POST","", a2)
# Parse and dump the JSON response from server
#objs = handle_response(conn)
#a2wc = objs['data']['wizCardID']

conn.request("POST","", a3)
# Parse and dump the JSON response from server
objs = handle_response(conn)
a3wc = objs['data']['wizCardID']

conn.request("POST","", a4)
# Parse and dump the JSON response from server
objs = handle_response(conn)
a4wc = objs['data']['wizCardID']

conn.request("POST","", a5)
# Parse and dump the JSON response from server
objs = handle_response(conn)
a5wc = objs['data']['wizCardID']

conn.request("POST","", a6)
# Parse and dump the JSON response from server
objs = handle_response(conn)
a6wc = objs['data']['wizCardID']
