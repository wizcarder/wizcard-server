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
    def __init__(self, data):
	self.data = data
	for element in data['elementList']:
	    notifType = element['notifType']
	    notifData = element['data']
	    self.process(notifType, notifData)

    def process(self, notifType, data):
        notifTableHandler = {
            ACCEPT_IMPLICIT: self.accept_implicit,
            ACCEPT_EXPLICIT: self.accept_explicit,
            DELETE_IMPLICIT: self.delete_implicit,
            TABLE_TIMEOUT:   self.table_timeout,
            UPDATE_WIZCARD:  self.update_wizcard,
            FLICKED_WIZCARD: self.flicked_wizcard,
            NEARBY_USERS   : self.nearby_users,
            NEARBY_TABLES  : self.nearby_tables,
            FLICK_TIMEOUT  : self.flick_timeout,
            FLICK_PICK     : self.flick_pick
        }

        return notifTableHandler[notifType](data)

    def accept_implicit(self, data):
        print "received accept implicit from",  data['user_id']
	pass

    def accept_explicit(self, data):
        print "received accept explicit from",  data['user_id']
	pass

    def delete_implicit(self, data):
        print "received delete implicit from"
	pass

    def table_timeout(self, data):
	pass

    def update_wizcard(self, data):
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

