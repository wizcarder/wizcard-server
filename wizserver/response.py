# define all outbound responses here
from wizcardship.models import WizConnectionRequest, Wizcard
from virtual_table.models import VirtualTable
from userprofile.models import UserProfile
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
        
    def add_data_array(self, d, count=1):
        if d:
            a = dict(data=d)
            self.response['data']['elementList'].append(a)
        self.response['data']['numElements'] += count
        return a

    def add_notif_type(self, d, type):
        d['notifType'] = type

    def add_data_with_notif(self, d, n, c=1):
        a = self.add_data_array(d, c)
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
    NEARBY_USERS        = 7
    NEARBY_TABLES       = 8

    def __init__(self):
        self.clear()

    def notifWizcard(self, notif, notifType):
        wizcard = Wizcard.objects.get(id=notif.target_object_id)
        out = Wizcard.objects.serialize(wizcard)
        self.add_data_with_notif(out, notifType)
        #AA:TODO: enhanced notification to carry wasEdited information
        if wizcard.thumbnailImage:
            self.add_data_to_dict(out, "thumbnailImage", wizcard.thumbnailImage.file.read())
        if wizcard.video:
            self.add_data_to_dict(out, "videoUrl", wizcard.video.url)
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

    def notifWizcardLookup(self, count, wizcards):
        out = None
        if wizcards:
            out = Wizcard.objects.serialize(wizcards)
        self.add_data_with_notif(out, self.FLICKED_WIZCARD, count)
        return self.response

    def notifUserLookup(self, count, users):
        out = None
        if users:
            out = UserProfile.objects.serialize(users)
            #AA:TODO: Not good if both dictionary have common names
        self.add_data_with_notif(out, self.NEARBY_USERS, count)
        return self.response

    def notifTableLookup(self, count, tables):
        out = None
        if tables:
            out = VirtualTable.objects.serialize(tables)
            #AA:TODO: Not good if both dictionary have common names
        self.add_data_with_notif(out, self.NEARBY_TABLES, count)
        return self.response


