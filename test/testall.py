#!/usr/bin/python

# Test WizCard client (the real one resides on a smartphone - iphone, android)

# Standard imports
import httplib
import json
import pdb
import messages
from notifications import NotifParser
import random
from random import randint
import string
import sys

numargs = len(sys.argv)

FUTURE_PHONE1 = "+11111111111"
FUTURE_PHONE2 = "+12222222222"
FUTURE_PHONE3 = "+13333333333"
FUTURE_PHONE4 = "+14444444444"
FUTURE_USERNAME1 = FUTURE_PHONE1+'@wizcard.com'
FUTURE_USERNAME2 = FUTURE_PHONE2+'@wizcard.com'
FUTURE_USERNAME3 = FUTURE_PHONE3+'@wizcard.com'
FUTURE_USERNAME4 = FUTURE_PHONE4+'@wizcard.com'
FUTURE_EMAIL1 = "abcd@future.com"
FUTURE_EMAIL2 = "efgh@future.com"
FUTURE_EMAIL3 = "ijkl@future.com"
FUTURE_EMAIL4 = "mnop@future.com"
DEVICE_ID4 = "dddddddddddddddddddddddddd"
FIRSTNAME_Q = "a"
uid_dict = {}
wuidlist = []
wizcardlist = []
flicklist = []
if numargs < 2:
    print "Usage testall.py <input file>"
    exit

#DATA_FILE = "/home/anand/testenv/wizcard-server/test/allfields.txt"
DATA_FILE = sys.argv[1]
TEST_IMAGE = False
test_image_path = "test/9-f_bc.81.2015-03-16_2213.jpg"

validreqs = {'phone_check_req' : 1}

data = open(DATA_FILE, "r")
NEXMO_PHONE="14084641727"
#server_url = "localhost"
server_url = "wizserver-lb-797719134.us-west-1.elb.amazonaws.com"
#server_port = 8000
server_port = 80

conn = httplib.HTTPConnection(server_url, server_port)

def handle_response(conn, msg_type):
    res = conn.getresponse()
    print res.status, res.reason
    objs = res.read()    
    objs = json.loads( objs )
    print "received respone for Message: ", msg_type
    print json.dumps(objs, sort_keys = True, indent = 2)
    return objs


for reqs in validreqs.keys():
    for l1 in data:
        (phone, deviceid, location,name) = l1.split('\t')
        ulocation = location.rstrip('\n')
        (lat,lng) = ulocation.split(',')
        (fname,lname) = name.rstrip('\n').split(' ')

        flat = float(lat)
        flng = float(lng)
        if reqs == 'phone_check_req':
            mesg = messages.phone_check_req
            mesg['header']['deviceID'] = deviceid
            mesg['header']['hash'] = deviceid
            mesg['sender']['username'] = phone + "@wizcard.com"
            mesg['sender']['responseMode'] = 'voice'
            mesg['sender']['target'] = NEXMO_PHONE
            mesg['sender']['test_mode'] = True
            req = json.dumps(mesg)

            conn.request("POST","", req)
            print "sending phone_check_req", req
# Parse and dump the JSON response from server
            objs = handle_response(conn, mesg['header']['msgType'])
            response_key = objs['data']['challenge_key']
            if response_key:
                mesg = messages.phone_check_resp
                mesg['header']['deviceID'] = deviceid
                mesg['header']['hash'] = deviceid
                mesg['sender']['username'] = phone + "@wizcard.com"
                mesg['sender']['responseKey'] = response_key
                req = json.dumps(mesg)
                conn.request("POST","", req)
                print "sending phone_check_rsp", req
# Parse and dump the JSON response from server
                objs = handle_response(conn, mesg['header']['msgType'])
                try:
                    uid1 = objs['data']['userID']
                    print "Successfully created UID =" + uid1
                    uid_dict[uid1]={}
                    uid_dict[uid1]['uid'] = uid1
                except KeyError, e:
                    print "KeyError: Creation of User fails for" + mesg['sender']['username']

                if uid1:

	                mesg = messages.login
	                mesg['sender']['username'] = phone + "@wizcard.com"
	                mesg['sender']['userID'] = uid1
	                mesg['header']['deviceID'] = deviceid
	                login = json.dumps(mesg)
	                print "sending login", login
	                conn.request("POST","", login)
	# Parse and dump the JSON response from server
	                objs = handle_response(conn, mesg['header']['msgType'])
	                wuid1 = objs['data']['wizUserID']

                        if wuid1:
                            uid_dict[uid1]['wuid'] = wuid1


                            mesg = messages.register1
                            mesg['sender']['userID']=uid1
                            mesg['sender']['wizUserID']=wuid1
                            mesg['sender']['lat']=flat
                            mesg['sender']['lng']=flng
                            r1 = json.dumps(mesg)
                            conn.request("POST","", r1)
                            print "sending register"
            # Parse and dump the JSON response from server
                            objs = handle_response(conn, mesg['header']['msgType'])

                            if TEST_IMAGE:
                                f = open(test_image_path, 'rb')
                                out = f.read().encode('hex')
                            else:
                                out = None

			    mesg = messages.edit_card1
			    mesg['sender']['userID'] = uid1
			    mesg['sender']['wizUserID'] = wuid1
                            mesg['sender']['phone'] = phone
                            mesg['sender']['email'] = phone + "@wizcard.com"
                            mesg['sender']['first_name'] = fname
                            mesg['sender']['last_name'] = lname

			    contacts = mesg['sender']['contact_container']
				#populate file
                            for c in contacts:
			     c['f_bizCardImage'] = out
			     c['b_bizCardImage'] = out

			    e1 = json.dumps(mesg)
			    print "sending EDIT CARD for", mesg['sender']['userID']
			    conn.request("POST","", e1)
			# Parse and dump the JSON response from server
			    objs = handle_response(conn, mesg['header']['msgType'])
			    e1_id = objs['data']['wizCardID']
                            if e1_id:
                                  uid_dict[uid1]['wizCardID'] = e1_id
                                  print "Created Wizcard " + str(e1_id)
                                  reqmsg = messages.location
                                  reqmsg['sender']['lat'] = flat
			          reqmsg['sender']['lng'] = flng
			          reqmsg['sender']['userID'] = uid1
			          reqmsg['sender']['wizUserID'] = wuid1
				  l1 = json.dumps(reqmsg)
				  print "sending Location Update for", reqmsg['sender']['userID']
				  conn.request("POST","", l1)
				# Parse and dump the JSON response from server
				  objs = handle_response(conn, reqmsg['header']['msgType'])
                                  reqmsg = messages.card_flick
                                  reqmsg['sender']['userID'] = uid1
                                  reqmsg['sender']['wizUserID'] = wuid1
                                  reqmsg['sender']['lat'] = flat
			          reqmsg['sender']['lng'] = flng
                                  print "flicking card", reqmsg['sender']['userID']
                                  cf1 = json.dumps(reqmsg)
                                  conn.request("POST","", cf1)
                                # Parse and dump the JSON response from server
                                  objs = handle_response(conn, reqmsg['header']['msgType'])
                                  cf1_id = objs['data']['flickCardID']

                                  if cf1_id:
                                      if 'flick' in uid_dict[uid1]:
                                        uid_dict[uid1]['flick'].append(cf1_id)
                                      else:
                                          uid_dict[uid1]['flick'] = cf1_id
                                                  
                                      print "Card Flicked: " + str(cf1_id)
                                  else:
                                      print "ERROR:Failed to flick"

                                  reqmsg = messages.card_flick
                                  reqmsg['sender']['userID'] = uid1
                                  reqmsg['sender']['wizUserID'] = wuid1

                                  print "re-flicking card from close-by location", reqmsg['sender']['userID']
                                  reqmsg['sender']['lng'] = flng+0.000001
                                  reqmsg['sender']['lat'] = flat+0.000001
                                  cf3 = json.dumps(reqmsg)
                                  conn.request("POST","", cf3)
# Parse and dump the JSON response from server
                                  objs = handle_response(conn, reqmsg['header']['msgType'])
                                  cf3_id = objs['data']['flickCardID']
                                  if cf3_id != cf1_id:
                                    print "ERROR in DELTA AGGLORMERATION"
                                 
                                  alluids = uid_dict.keys()
                                  if len(alluids) > 1:
	                                  uid_rand = uid1
	                                  while uid_rand == uid1:
	                                    uid_index = randint(0, len(alluids)-1)
	                                    uidpair = alluids[uid_index]
	                                    uid_rand = uid_dict[uidpair]['uid']
	
	
	                                  reqmsg = messages.card_flick_accept
	                                  reqmsg['sender']['userID'] = uid_dict[uidpair]['uid']
	                                  reqmsg['sender']['wizUserID'] = uid_dict[uidpair]['wuid']
	                                  reqmsg['receiver']['flickCardIDs'] = [cf3_id]
	                                  print "sending flick accept"
	                                  cfa1 = json.dumps(reqmsg)
	                                  conn.request("POST","", cfa1)
	                    # Parse and dump the JSON response from server
	                                  objs = handle_response(conn, reqmsg['header']['msgType'])

                                  print "checking flick pickers"
                                  reqmsg = messages.flick_pickers
                                  reqmsg['sender']['userID'] = uid1
                                  reqmsg['sender']['wizUserID'] = wuid1
                                  reqmsg['sender']['flickCardID'] = cf3_id
                                  fp3 = json.dumps(reqmsg)
                                  conn.request("POST","", fp3)
                                  # Parse and dump the JSON response from server
                                  objs = handle_response(conn, reqmsg['header']['msgType'])
 
                                  print "retrieving myFlicks"
                                  reqmsg = messages.my_flicks
                                  reqmsg['sender']['userID'] = uid1
                                  reqmsg['sender']['wizUserID'] = wuid1
                                  reqmsg['sender']['wizCardID'] = e1_id
                                  mcf1 = json.dumps(reqmsg)
                                  conn.request("POST","", mcf1)
 #arse and dump the JSON response from server
                                  objs = handle_response(conn, reqmsg['header']['msgType'])

				   #user query
                                  reqmsg = messages.user_query
                                  reqmsg['sender']['userID'] = uid1
				  reqmsg['sender']['wizUserID'] = wuid1
				  reqmsg['receiver']['name'] = FIRSTNAME_Q
				  uq = json.dumps(reqmsg)
				  conn.request("POST","", uq)
				  # Parse and dump the JSON response from server
				  objs = handle_response(conn, reqmsg['header']['msgType'])

			           #flick query
			          reqmsg = messages.card_flick_query
			          reqmsg['sender']['userID'] = uid1
			          reqmsg['sender']['wizUserID'] = wuid1
			          reqmsg['receiver']['name'] = FIRSTNAME_Q
			          fq3 = json.dumps(reqmsg)
			          conn.request("POST","", fq3)
			# Parse a dump the JSON response from server
			          objs = handle_response(conn, reqmsg['header']['msgType'])
			
                                  TABLE1NAME = "One"
                                  TABLE1NAME_NEW = "One More"

                                  print "Creating Table one"
                                  reqmsg = messages.table_create
                                  reqmsg['sender']['userID'] = uid1
                                  reqmsg['sender']['wizUserID'] = wuid1
                                  reqmsg['sender']['table_name'] = TABLE1NAME
                                  reqmsg['sender']['timeout'] = 1
                                  tbl_c_1 = json.dumps(reqmsg)
                                  conn.request("POST","", tbl_c_1)
                                  # Parse and dump the JSON response from server
                                  objs = handle_response(conn, reqmsg['header']['msgType'])
                                  tid_1 = objs['data']['tableID']

                                  if tid_1:
                                    uid_dict[uid1]['table'] = tid_1


                                    #join created table
                                    print "Joining Table"
                                  # Create a function to return random values given a keytype
                                    alluids = uid_dict.keys()
                                    if len(alluids) > 1:
	                                    uid_rand = uid1
	
	                                    while uid_rand == uid1:
	                                        uid_index1 = randint(0, len(alluids)-1)
	                                        uid_rand = uid_dict[alluids[uid_index1]]['uid']
	                                        wuid_rand = uid_dict[alluids[uid_index1]]['wuid']
	
	                                    reqmsg = messages.table_join
	                                    reqmsg['sender']['userID'] = uid_rand
	                                    reqmsg['sender']['wizUserID'] = wuid_rand
	                                    reqmsg['sender']['tableID'] = tid_1
	                                    tbl_j_1 = json.dumps(reqmsg)
	                                    conn.request("POST","", tbl_j_1)
	                                    # Parse and dump the JSON response from server
	                                    objs = handle_response(conn, reqmsg['header']['msgType'])
	
	                                    print "Joining Table with error password"
	                                    alluids = uid_dict.keys()
	                                    uid_rand = uid1
	
	                                    while uid_rand == uid1:
	                                        uid_index1 = randint(0, len(alluids)-1)
	                                        uid_rand = uid_dict[alluids[uid_index1]]['uid']
	                                        wuid_rand = uid_dict[alluids[uid_index1]]['wuid']
	
	                                    reqmsg = messages.table_join
	                                    reqmsg['sender']['userID'] = uid_rand
	                                    reqmsg['sender']['wizUserID'] = wuid_rand
	                                    reqmsg['sender']['tableID'] = tid_1
	                                    reqmsg['sender']['password'] = "xxx"
	                                    tbl_j_1 = json.dumps(reqmsg)
	                                    # Parse and dump the JSON response from server
	                                    conn.request("POST","", tbl_j_1)
	                                    objs = handle_response(conn, reqmsg['header']['msgType'])
	
                                    print "Edit Table" 
                                    reqmsg = messages.table_edit
                                    reqmsg['sender']['userID'] = uid1
                                    reqmsg['sender']['wizUserID'] = wuid1
                                    reqmsg['sender']['tableID'] = tid_1
                                    reqmsg['sender']['oldName'] = TABLE1NAME
                                    TABLE1NAME_NEW = "VTABLE1_NEW"
                                    reqmsg['sender']['newName'] = TABLE1NAME_NEW
                                    reqmsg['sender']['timeout'] = 5
                                    tbl_e_1 = json.dumps(reqmsg)
                                    # Parse and dump the JSON response from server
                                    conn.request("POST","", tbl_e_1)
                                    objs = handle_response(conn, reqmsg['header']['msgType'])


                                    alluids = uid_dict.keys()
                                    if len(alluids) > 1:
	                                    uid_rand = uid1
	
	                                    while uid_rand == uid1:
	                                        uid_index1 = randint(0, len(alluids)-1)
	                                        uid_rand = uid_dict[alluids[uid_index1]]['uid']
	                                        wuid_rand = uid_dict[alluids[uid_index1]]['wuid']
	
	                                    #table query
	                                    print "sending table query"
	                                    TABLENAME_Q = "one"
	                                    reqmsg = messages.table_query
	                                    reqmsg['sender']['userID'] = uid_rand
	                                    reqmsg['sender']['wizUserID'] = wuid_rand
	                                    reqmsg['receiver']['name'] = TABLENAME_Q
	                                    tq3 = json.dumps(reqmsg)
	                                    conn.request("POST","", tq3)
	                                    # Parse and dump the JSON response from server
	                                    objs = handle_response(conn, reqmsg['header']['msgType'])
	
	                                    #table summary
	                                    print "sending table summary"
	                                    reqmsg = messages.table_summary
	                                    reqmsg['sender']['userID'] = uid1
	                                    reqmsg['sender']['wizUserID'] = wuid1
	                                    reqmsg['sender']['tableID'] = tid_1
	                                    ts3 = json.dumps(reqmsg)
	                                    conn.request("POST","", ts3)
	                                    # Parse and dump the JSON response from server
	                                    objs = handle_response(conn, reqmsg['header']['msgType'])
	
	                                    #table details
	                                    print "sending table details"
	                                    reqmsg = messages.table_details
	                                    reqmsg['sender']['userID'] = uid1
	                                    reqmsg['sender']['wizUserID'] = wuid1
	                                    reqmsg['sender']['tableID'] = tid_1
	                                    td3 = json.dumps(reqmsg)
	                                    conn.request("POST","", td3)
	                                    # Parse and dump the JSON response from server
	                                    objs = handle_response(conn, reqmsg['header']['msgType'])
                                  alluids = uid_dict.keys()
                                  if len(alluids) > 1:
                                    #delete rolodex card
	                                  print "deleting all cards of ", uid1
	                                  reqmsg = messages.delete_rolodex_card
	                                  reqmsg['sender']['userID'] = uid1
	                                  reqmsg['sender']['wizUserID'] = wuid1
	                                  alluids = uid_dict.keys()
	                                  (uid_index1,uid_index2) = (randint(0, len(alluids)-1), randint(0,len(alluids)-1))
	                                  (wcid1, wcid2) = (uid_dict[alluids[uid_index1]]['wizCardID'], uid_dict[alluids[uid_index2]]['wizCardID'])
	
	
	                                  reqmsg['receiver']['wizCardIDs'] = [wcid1,wcid2]
	                                  dc1 = json.dumps(reqmsg)
	                                  conn.request("POST","", dc1)
	                                    # Parse and dump the JSON response from server
	                                  objs = handle_response(conn, reqmsg['header']['msgType'])


                                  print "get cards for user", uid1
                                  reqmsg = messages.get_cards
                                  reqmsg['sender']['userID'] = uid1
                                  reqmsg['sender']['wizUserID'] = wuid1
                                  print "GET cards", reqmsg['sender']['userID']
                                  gcu1 = json.dumps(reqmsg)
                                  conn.request("POST","", gcu1)
                                  # Parse and dump the JSON response from server
                                  objs = handle_response(conn, reqmsg['header']['msgType'])
                                  notif = NotifParser(objs['data'], uid1, wuid1)
                                  nrsp = notif.process_one()
                                  while nrsp != False:
                                    if nrsp is not None:
                                       nrsp = json.dumps(nrsp)
                                       conn.request("POST","", n)
        # Parse and dump the JSON response from server
                                       objs = handle_response(conn, reqmsg['header']['msgType'])
                                    nrsp = notif.process_one()

                                  reqmsg = messages.card_details
                                  reqmsg['sender']['userID'] = uid1
                                  reqmsg['sender']['wizUserID'] = wuid1
                                  reqmsg['receiver']['wizCardID'] = e1_id
                                  print "GET card DETAILS", reqmsg['sender']['userID']
                                  cd1 = json.dumps(reqmsg)
                                  conn.request("POST","", cd1)
# Parse and dump the JSON response from server
                                  objs = handle_response(conn, reqmsg['header']['msgType'])
       				  #assetToXYZ tests
    				  #asset types: wizcard, table
                                  #receiverType: phone, email, wizUserID
                                  alluids = uid_dict.keys()
                                  if len(alluids) > 1:
                                    uid_rand = uid1
	                            while uid_rand == uid1:
	                             uid_index1 = randint(0, len(alluids)-1)
	                             uid_rand = uid_dict[alluids[uid_index1]]['uid']
	                             wuid_rand = uid_dict[alluids[uid_index1]]['wuid']
    				
    				  #u1 -> u2, u3 via wiz
      				     reqmsg = messages.send_asset_to_xyz
      				     reqmsg['sender']['userID'] = uid1
      				     reqmsg['sender']['wizUserID'] = wuid1
      				     reqmsg['sender']['assetID'] = e1_id
      				     reqmsg['sender']['assetType'] = "wizcard"
      				     reqmsg['receiver']['receiverType'] = "wiz_untrusted"
      				     reqmsg['receiver']['receiverIDs'] = [wuid_rand]
      				     print "sendingWizcardToUnTrusted"
      				     sxyz = json.dumps(reqmsg)
      				     conn.request("POST","", sxyz)
      				  # Parse and dump the JSON response from server
      				     objs = handle_response(conn, reqmsg['header']['msgType'])
      				
      				
      				  #u1 -> future_u1, u2 via sms
      				  reqmsg = messages.send_asset_to_xyz
      				  reqmsg['sender']['userID'] = uid1
      				  reqmsg['sender']['wizUserID'] = wuid1
      				  reqmsg['sender']['assetID'] = e1_id
      				  reqmsg['sender']['assetType'] = "wizcard"
      				  reqmsg['receiver']['receiverType'] = "sms"
      				  reqmsg['receiver']['receiverIDs'] = [FUTURE_PHONE1, FUTURE_PHONE2]
      				  print "sendingWizcardToSMS"
      				  sxyz = json.dumps(reqmsg)
      				  conn.request("POST","", sxyz)
      				  # Parse and dump the JSON response from server
      				  objs = handle_response(conn, reqmsg['header']['msgType'])
      		      		
      		  		  #u2 -> future u1, u2 via email
      				  reqmsg['sender']['userID'] = uid1
      				  reqmsg['sender']['assetType'] = "wizcard"
      				  reqmsg['sender']['wizUserID'] = wuid1
      				  reqmsg['sender']['assetID'] = e1_id
      				  reqmsg['receiver']['receiverType'] = "email"
      				  reqmsg['receiver']['receiverIDs'] = [FUTURE_EMAIL1, FUTURE_EMAIL2]
      				  print "sendingWizcardToEMAIL"
      				  sxyz = json.dumps(reqmsg)
      				  conn.request("POST","", sxyz)
      				  # Parse and dump the JSON response from server
      				  objs = handle_response(conn, reqmsg['header']['msgType'])
      				
      				  #now create future u1 and u2
      				
      				  print "creating future user 1 and 2"
      				  reqmsg = messages.phone_check_req
      				  reqmsg['header']['deviceID'] = DEVICE_ID4
      				  reqmsg['header']['hash'] = deviceid
      				  reqmsg['sender']['username'] = FUTURE_USERNAME1
      				  reqmsg['sender']['target'] = FUTURE_PHONE1
      				  reqmsg['sender']['responseMode'] = 'sms'
      				  reqmsg['sender']['test_mode'] = True
      				  pcreq2 = json.dumps(reqmsg)
      				  conn.request("POST","", pcreq2)
      				  print "sending phone_check_req", pcreq2
      				  # Parse and dump the JSON response from server
      				  objs = handle_response(conn, reqmsg['header']['msgType'])
      				  response_key = objs['data']['challenge_key']
    		
  
  
	
                            else:
                                print "ERROR:Cannot create wizcard for " + wuid1
				
                        else:
                            print "ERROR:Cannot create wizuserid"
                else:
                    print "ERROR:Cannot create User for phone"



