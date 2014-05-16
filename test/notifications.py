import pdb

ACCEPT_IMPLICIT     = 1
ACCEPT_EXPLICIT     = 2
DELETE_IMPLICIT     = 3
TABLE_TIMEOUT       = 4
UPDATE_WIZCARD      = 5
FLICKED_WIZCARD     = 6
NEARBY_USERS        = 7
NEARBY_TABLES       = 8
FLICK_TIMEOUT       = 9
FLICK_PICK	    = 10

class NotifParser:
    def __init__(self, userID, wizUserID):
	pdb.set_trace()
	self.data = self['data']
	self.userID = userID
	self.wizUserID = wizUserID
	self.notifType = []
	self.notifData = []
	self.count = 0
	for element in elementList:
	    self.notifType.append(element['notifType'])
	    self.notifData.append(element['data'])
	    self.count += 1

    def process_one():
	if self.count:
	    self.count -= 1
            return self.notifTableHandler[self.notifType.pop()](self.notifData.pop())
        else:
            return False
        

    def accept_implicit(data):
        print "received accept implicit from" data.user_id
	pass

    def accept_explicit(data):
        print "received accept explicit from" data.user_id
	rsp = message.add_notification_card
	rsp['receiver']['wizUserID'] = data['wizUserID']
	return rsp

    def delete_implicit(data):
        print "received delete implicit from" data.user_id
	pass

    def table_timeout(data):
        print "received table timeout from" data.id
	pass

    def update_wizcard(data):
	pass

    def flicked_wizcard(self, data):
        if data.has_key('connected'):
            print "own flicked wizcard", map(lambda w: w['flick_id'], data['connected'])
	pass

    def nearby_users(self, data):
	pass

    def nearby_tables(self, data):
	pass

    def flick_timeout(self, data):
	pass

    def flick_pick(self, data):
	pass

