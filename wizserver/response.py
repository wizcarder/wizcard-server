# define all outbound responses here
from wizcardship.models import WizConnectionRequest, Wizcard
from json_wrapper import DataDumper
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
        self.response['data']['numElements'] = 0
        self.response['data']['elementList'] = []
        
    def add_data(self, d, c):
        a = dict(data=d)
        self.response['data']['elementList'].append(a)
        self.response['data']['numElements'] += c
        return a

    def add_notif_type(self, d, type):
        d['notifType'] = type

    def add_data_with_notif(self, d, n, c):
        a = self.add_data(d, c)
        self.add_notif_type(a, n)


class NotifResponse(ResponseN):

    ACCEPT_IMPLICIT     = 0
    ACCEPT_EXPLICIT     = 1
    DELETE_IMPLICIT     = 2

    NOTIF_NULL                      = 0
    NOTIF_WIZCARD_ADD_ROLODEX       = 1
    NOTIF_WIZCARD_ADD_NOTIFICATION  = 2
    NOTIF_WIZCARD_DEL               = 3

    notifMapping = {
        ACCEPT_IMPLICIT : NOTIF_WIZCARD_ADD_ROLODEX,
        ACCEPT_EXPLICIT : NOTIF_WIZCARD_ADD_NOTIFICATION,
        DELETE_IMPLICIT  : NOTIF_WIZCARD_DEL
    }



    def __init__(self):
        self.clear()

    def notifWizcard(self, notif, accept):
        wizcard = Wizcard.objects.get(id=notif.target_object_id)
        dumper = DataDumper()
        fields = ["id", "company", "title", "phone1", 
                  "phone2", "email", "address_street1", "address_city",
                  "address_state", "address_country", "address_zip"]
        dumper.selectObjectFields('Wizcard', fields)
        out = dumper.dump(wizcard, 'json')
        self.add_data_with_notif(out, self.notifMapping[accept], 1)
        return self.response

    def notifWizConnectionT(self, notif):
        return self.notifWizcard(notif, self.ACCEPT_IMPLICIT)

    def notifWizConnectionU(self, notif):
        return self.notifWizcard(notif, self.ACCEPT_EXPLICIT)

    def notifAcceptedWizcard(self, notif):
        return self.notifWizConnectionT(notif)

    def notifRevokedWizcard(self, notif):
        #this is a notif to the app B when app A removed B's card
        out = dict(wizCardId=notif.target_object_id)
        self.add_data_with_notif(out, self.notifMapping[self.DELETE_IMPLICIT], 1)
        return self.response
