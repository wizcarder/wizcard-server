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
        
    def add_data(self, d, n):
        a = dict(data=d, notifType=n)
        self.response['data']['elementList'].append(a)
        self.response['data']['numElements'] += 1

    def add_notif_type(self, type):
        self.response['data']['notifType'] = type

class NotifResponse(ResponseN):

    NOTIF_WIZCARD_ADD_ROLODEX       = 1
    NOTIF_WIZCARD_ADD_NOTIFICATION  = 2
    NOTIF_WIZCARD_DEL               = 3

    ACCEPT_IMPLICIT     = 0
    ACCEPT_EXPLICIT     = 1

    notifMapping = {
        ACCEPT_IMPLICIT : NOTIF_WIZCARD_ADD_ROLODEX,
        ACCEPT_EXPLICIT : NOTIF_WIZCARD_ADD_NOTIFICATION
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
        self.add_data(out, self.notifMapping[accept])
        return self.response

    def notifWizConnectionT(self, notif):
        return self.notifWizcard(notif, self.ACCEPT_IMPLICIT)

    def notifWizConnectionU(self, notif):
        return self.notifWizcard(notif, self.ACCEPT_EXPLICIT)

    def notifAcceptedWizcard(self, notif):
        return self.notifWizconnectionT(self, notif)

    def notifRevokedWizcard(self, notif):
        #this is a notif to the app B when app A removed B's card

        obj = Wizcard.objects.get(id=notif.target_object_id)
        out = dict(wizCardId=obj.id)
        self.add_data(out, self.NOTIF_WIZCARD_DEL)
        return self.response


