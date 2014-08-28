import pdb
import messages

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
    def __init__(self, data, userID, wizUserID):
	self.data = data
	self.userID = userID
	self.wizUserID = wizUserID
	self.notifType = []
	self.notifData = []
	self.count = 0
	for element in self.data['elementList']:
	    self.notifType.append(element['notifType'])
	    self.notifData.append(element['data'])
	    self.count += 1

    def process_one(self):
        notifTableHandler = {
            ACCEPT_IMPLICIT :       self.accept_implicit,
            ACCEPT_EXPLICIT :       self.accept_explicit,
            DELETE_IMPLICIT :       self.delete_implicit,
            TABLE_TIMEOUT   :       self.table_timeout,
            UPDATE_WIZCARD  :       self.update_wizcard,
            FLICKED_WIZCARD :       self.flicked_wizcard,
            NEARBY_USERS    :       self.nearby_users,
            NEARBY_TABLES   :       self.nearby_tables,
            FLICK_TIMEOUT   :       self.flick_timeout
        }

	if self.count:
	    self.count -= 1
            return notifTableHandler[self.notifType.pop()](self.notifData.pop())
        else:
            return False
        

    def accept_implicit(self, data):
        print "received accept implicit from", data['user_id']
	pass

    def accept_explicit(self, data):
        print "received accept explicit from", data['user_id']
	#rsp = messages.add_notification_card
	#rsp['receiver']['wizUserID'] = data['wizUserID']
	pass

    def delete_implicit(self, data):
        print "received delete implicit from", data['user_id']
	pass

    def table_timeout(self, data):
        print "received table timeout from", data
	pass

    def update_wizcard(self, data):
	pass

    def flicked_wizcard(self, data):
        if data.has_key('connected'):
            print "own flicked wizcard", map(lambda w: w['flick_id'], data['connected'])

    def nearby_users(self, data):
	pass

    def nearby_tables(self, data):
	pass

    def flick_timeout(self, data):
	pass

    def flick_pick(self, data):
	pass

