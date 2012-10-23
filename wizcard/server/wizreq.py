#!/usr/bin/python
# The Wiz Server:
# Implements the core message handling functionality.

# Required standard imports
import json

# Required Wiz specific imports
import wizutils
import pdb

# TODO: Eventually remove these test messages
ack  = {"status": "ok"}
nack = {"status": "fail"}
user_profile_card = {
        "userID":       "thewizkid",
        "first":        "anand",
        "last":         "ammundi",
        "company":      "wiz inc.",
        "title":        "founder",
        "phone":        "(408)-xxx-yyyy",
        "email":        "thewizkid@whiz.selfip.com",
        "street":       "dunholme ave",
        "city":         "sunnyvale",
        "state":        "california",
        "zip":          "94087",
        "location":     [{"lat":37.32300, "lng":-122.03218}]
        }

# All Wiz requests are handled by this class
class WizRequestHandler:
    # In-core dictionary of active users
    active_users = {}

    def __init__(self, db):
        self.db = db
	# TODO: preload active_users from DB (server might have crashed)

    # Process register message
    def processRegister(self, message):
        wizutils.log('Received register request: ', message)
	# 1. Register the fact that this user is active
	key = message['userID'].encode('utf-8')
	if self.active_users.has_key(key):
	    wizutils.log('duplicate registration for user ', key)
	else:
	    regdict = {}
	    regdict['userID'] = key
	    #regdict['lat'] = message['message'][0]['lat']
	    #regdict['lng'] = message['message'][0]['lng']
	    regdict['lat'] = message['message']['lat']
	    regdict['lng'] = message['message']['lng']
	    #self.db.insertDict('registrations', regdict)
	    #self.active_users[key] = regdict
	
	# 2. Return the list of business cards
	# TODO: exception handling - maybe on client side - empty list
	return self.db.except_query('wiz_card_user', 'userid', message['userID'])

    def processLocationUpdate(self, message):
        wizutils.log(message)

    def processAcceptCard(self, message):
        wizutils.log(message)

    def processDeleteCard(self, message):
        wizutils.log(message)

    def processRequest(self, request):
        msgHandlers = {
            'register' : self.processRegister,
            'update'   : self.processLocationUpdate,
            'accept'   : self.processAcceptCard,
            'delete'   : self.processDeleteCard,
            # TODO more message handlers
        }

        # debugging 
        wizutils.log(request)

        # Dispatch to appropriate message handler
        return msgHandlers[request['msgType']](request)

# End of wizreq.py
