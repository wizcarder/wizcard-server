# define all outbound responses here
from wizcardship.models import WizConnectionRequest, Wizcard
from json_wrapper import DataDumper
import fields
import pdb

#This is the basic Response class used to send simple result and data
class Response:
    response = {
        "result" : {
        },
        "data" : {
        }
    }

    def __init__(self):
        self.response['result'].clear()
        self.response['data'].clear()
        self.response['result']['Error'] = 0

    def add_result(self, k, v):
        self.response['result'][k] = v

    def add_data(self, k, v):
        self.response['data'][k] = v

    def error_response(self, errno, errorStr):
        self.add_result("Error", errno)
        self.add_result("Description", errorStr)
        self.response
        
#subclass of above. This handles arrays of Data and used by Notifications
class ResponseN(Response):
    response = {
        "result" : {
        },
        "data" : {
            "numElements" : 0,
            "elementList" : []
        }
    }

    def clear(self):
        self.response['result']['Error'] = "0"
        self.response['result']['Description'] = "Ok"
        self.response['data'] = {}
        self.response['data']['numElements'] = 0
        self.response['data']['elementList'] = []
        
    def add_data_array(self, d):
        a = dict(data=d)
        self.response['data']['elementList'].append(a)
        self.response['data']['numElements'] += 1
        return a

    def add_notif_type(self, d, type):
        d['notifType'] = type

    def add_data_with_notif(self, d, n):
        a = self.add_data_array(d)
        self.add_notif_type(a, n)
    
    def add_data_to_dict(self, dict, k, v):
        dict[k] = v


class NotifResponse(ResponseN):

    NOTIF_NULL          = 0
    ACCEPT_IMPLICIT     = 1
    ACCEPT_EXPLICIT     = 2
    DELETE_IMPLICIT     = 3
    DELETE_TABLE        = 4
    UPDATE_WIZCARD      = 5
    FLICKED_WIZCARD     = 6

    def __init__(self):
        self.clear()

    def notifWizcard(self, notif, notifType):
        wizcard = Wizcard.objects.get(id=notif.target_object_id)
        out = Wizcard.objects.serialize(wizcard)
        self.add_data_to_dict(out, "user_id", notif.actor_object_id)
        self.add_data_with_notif(out, notifType)
        if wizcard.thumbnailImage:
            self.add_data_to_dict(out, "thumbnailImage", wizcard.thumbnailImage.file.read())
        print "sending wizcard notification"
        return self.response

    def notifWizConnectionT(self, notif):
        return self.notifWizcard(notif, self.ACCEPT_IMPLICIT)

    def notifWizConnectionU(self, notif):
        return self.notifWizcard(notif, self.ACCEPT_EXPLICIT)

    def notifAcceptedWizcard(self, notif):
        return self.notifWizConnectionT(notif)

    def notifRevokedWizcard(self, notif):
        #this is a notif to the app B when app A removed B's card
        out = dict(user_id=notif.actor_object_id)
        self.add_data_with_notif(out, self.DELETE_IMPLICIT)
        print "sending revoke notification"
        print self.response
        return self.response

    def notifDestroyedTable(self, notif):
        out = dict(tableID=notif.target_object_id)
        self.add_data_with_notif(out, self.DELETE_TABLE)
        print self.response
        return self.response

    def notifWizcardUpdate(self, notif):
        return self.notifWizcard(notif, self.UPDATE_WIZCARD)

    def notifWizcardLookup(self, wizcards):
        out = Wizcard.objects.serialize(wizcards)
        self.add_data_with_notif(out, self.FLICKED_WIZCARD)
        return self.response


