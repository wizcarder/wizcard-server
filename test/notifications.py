import pdb
import sys
proj_path="."
sys.path.append(proj_path)
from wizserver import verbs


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
            verbs.NOTIF_ACCEPT_IMPLICIT :       self.accept_implicit,
            verbs.NOTIF_ACCEPT_EXPLICIT :       self.accept_explicit,
            verbs.NOTIF_DELETE_IMPLICIT :       self.delete_implicit,
            verbs.NOTIF_TABLE_TIMEOUT   :       self.table_timeout,
            verbs.NOTIF_UPDATE_WIZCARD  :       self.update_wizcard,
            verbs.NOTIF_NEARBY_FLICKED_WIZCARD :       self.flicked_wizcard,
            verbs.NOTIF_NEARBY_USERS    :       self.nearby_users,
            verbs.NOTIF_NEARBY_TABLES   :       self.nearby_tables,
            verbs.NOTIF_FLICK_TIMEOUT   :       self.flick_timeout,
            verbs.NOTIF_FLICK_PICK      :       self.flick_pick,
            verbs.NOTIF_WITHDRAW_REQUEST   :    self.withdraw_request,
            verbs.NOTIF_TABLE_INVITE    :       self.table_invite,
            verbs.NOTIF_WIZCARD_FORWARD :       self.wizcard_forward,
            verbs.NOTIF_ENTITY_JOIN :           self.table_join,
            verbs.NOTIF_ENTITY_LEAVE :          self.table_leave,
        }

        if self.count:
            self.count -= 1
            notifTableHandler[self.notifType.pop()](self.notifData.pop())
            return True
        else:
            return False

    def process(self):
        while True:
            nrsp = self.process_one()
            if not nrsp:
                break

    def accept_implicit(self, data):
        print "received accept implicit from", data['wizuser_id']
        pass

    def accept_explicit(self, data):
        print "received accept explicit from", data['wizuser_id']
        #rsp = messages.add_notification_card
        #rsp['receiver']['wizUserID'] = data['wizUserID']
        pass

    def delete_implicit(self, data):
        print "received delete implicit from", data['wizuser_id']
        pass

    def table_timeout(self, data):
        print "received table timeout from", data
        pass

    def table_join(self, data):
        print "received table join from", data
        pass

    def table_leave(self, data):
        print "received table leave from", data
        pass

    def update_wizcard(self, data):
        print "received update_wizcard", data
        pass

    def flicked_wizcard(self, data):
        if data.has_key('connected'):
            print "own flicked wizcard", map(lambda w: w['flick_id'], data['connected'])

    def nearby_users(self, data):
        print "received nearby users", data
        pass

    def nearby_tables(self, data):
        print "received nearby_tables", data
        pass

    def flick_timeout(self, data):
        print "received flick timeout ", data
        pass

    def flick_pick(self, data):
        print "received flick pick ", data
        pass

    def withdraw_request(self, data):
        print "received withdraw request ", data
        pass

    def table_invite(self, data):
        print "received table invite ", data
        pass

    def wizcard_forward(self, data):
        print "received wizcard forward ", data
        pass
