
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
    def __init__(self):
	pdb.set_trace()
	self.data = self['data']
	for element in elementList:
	    notifType = element['notifType']
	    notifData = element['data']
	    self.process(notifType, notifData)
    def process(notifType, data):
	pdb.set_trace()
        return self.notifTableHandler['notifType'](notifData)

    def accept_implicit(data):
	pdb.set_trace()
        print "received accept implicit from" data.user_id
	pass

    def accept_explicit(data):
	pdb.set_trace()
        print "received accept explicit from" data.user_id
	pass

    def delete_implicit(data):
	pdb.set_trace()
	pass

    def table_timeout(data):
	pdb.set_trace()
	pass

    def update_wizcard(data):
	pdb.set_trace()
	pass

    def flicked_wizcard(data):
	pdb.set_trace()
	pass

    def nearby_users(data):
	pdb.set_trace()
	pass

    def nearby_tables(data):
	pass

    def flick_timeout(data):
	pass

    def flick_pick(data):
	pass



	    
        


