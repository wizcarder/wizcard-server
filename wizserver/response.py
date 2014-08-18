# define all outbound responses here
from django.contrib.contenttypes.models import ContentType
from wizcardship.models import WizConnectionRequest, Wizcard, WizcardFlick
from virtual_table.models import VirtualTable
from userprofile.models import UserProfile
from notifications.models import Notification
from django.http import HttpResponse
import logging
import fields
import json
import pdb
from wizcard import err

logger = logging.getLogger("wizcard")
class errMsg:

    def __init__(self, err):
	self.errno = err[errno]
	self.description = err[str]
	

#This is the basic Response class used to send simple result and data
class Response:

    def __init__(self):
        self.response = dict(result=dict(Error=0, Description=""), data=dict())

    def __repr__(self):
        return json.dumps(self.response)

    def respond(self):
        ret = json.dumps(self.response) if self.response else None
        return HttpResponse(ret)

    def add_result(self, k, v):
        self.response['result'][k] = v

    def add_data(self, k, v):
        self.response['data'][k] = v

    def error_response(self, err):
        self.add_result("Error", err['errno'])
        self.add_result("Description", err['str'])
        return self

    def ignore(self):
        self.response = None
        return self
    
    def is_error_response(self):
        if not self.response or self.response['result']['Error']:
            return True
        return False
        
#subclass of above. This handles arrays of Data and used by Notifications
class ResponseN(Response):
    def __init__(self):
        Response.__init__(self)
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
    TABLE_TIMEOUT       = 4
    UPDATE_WIZCARD      = 5
    FLICKED_WIZCARD     = 6
    NEARBY_USERS        = 7
    NEARBY_TABLES       = 8
    FLICK_TIMEOUT       = 9
    FLICK_PICK	        = 10
    WITHDRAW_REQUEST    = 11

    def __init__(self, notifications):
        ResponseN.__init__(self)
        notifHandler = {
            Notification.WIZREQ_U 	            : self.notifWizConnectionU,
            Notification.WIZREQ_T  	            : self.notifWizConnectionT,
            Notification.WIZCARD_ACCEPT             : self.notifAcceptedWizcard,
            Notification.WIZCARD_REVOKE	            : self.notifRevokedWizcard,
            Notification.WIZCARD_WITHDRAW_REQUEST   : self.notifWithdrawRequest,
            Notification.WIZCARD_DELETE	            : self.notifRevokedWizcard,
            Notification.WIZCARD_TABLE_TIMEOUT      : self.notifDestroyedTable,
            Notification.WIZCARD_TABLE_DESTROY      : self.notifDestroyedTable,
            Notification.WIZCARD_UPDATE             : self.notifWizcardUpdate,
            Notification.WIZCARD_FLICK_TIMEOUT      : self.notifWizcardFlickTimeout,
            Notification.WIZCARD_FLICK_PICK         : self.notifWizcardFlickPick
        }
	for notification in notifications:
	    notifHandler[notification.verb](notification)
	    
    def notifWizcard(self, notif, notifType):
        wizcard = Wizcard.objects.get(id=notif.target_object_id)
        out = Wizcard.objects.serialize(wizcard,
                fields.wizcard_template_full)
        #AA:TODO: enhance notification to carry wasEdited information
        if wizcard.video:
            self.add_data_to_dict(out, "videoUrl", wizcard.video.url)

        #AA:TODO: looks ugly like this...structure it
	if notif.action_object:
            if ContentType.objects.get_for_model(notif.action_object) == ContentType.objects.get(model="wizcardflick"):
                    self.add_data_to_dict(out, "flickCardID", 
                            notif.action_object_object_id)
            elif ContentType.objects.get_for_model(notif.action_object) == ContentType.objects.get(model="virtualtable"):
                    self.add_data_to_dict(out, "tableID", 
                            notif.action_object_object_id)
                    try:
                        num_sitting = VirtualTable.objects.get(id=notif.action_object_object_id).numSitting
                    except:
                        num_sitting = 0
                    self.add_data_to_dict(out, "numSitting", num_sitting)

        self.add_data_with_notif(out, notifType)
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
        return self.response

    def notifWithdrawRequest(self, notif):
        #this is a notif to the app B when app A withdraws it's connection request
        out = dict(user_id=notif.actor_object_id)
        self.add_data_with_notif(out, self.WITHDRAW_REQUEST)
        logger.debug('%s', self.response)
        return self.response

    def notifDestroyedTable(self, notif):
        out = dict(tableID=notif.target_object_id)
        self.add_data_with_notif(out, self.TABLE_TIMEOUT)
        logger.debug('%s', self.response)
        return self.response

    def notifWizcardUpdate(self, notif):
        return self.notifWizcard(notif, self.UPDATE_WIZCARD)

    def notifWizcardFlickTimeout(self, notif):
	out = dict(flickCardID=notif.target_object_id)
        self.add_data_with_notif(out, self.FLICK_TIMEOUT)
        logger.debug('%s', self.response)
        return self.response

    def notifWizcardFlickPick(self, notif):
        out = dict(wizUserID=notif.action_object_object_id, flickCardID=notif.target_object_id)
        self.add_data_with_notif(out, self.FLICK_PICK)
        logger.debug('%s', self.response)
        return self.response

    def notifFlickedWizcardsLookup(self, count, user, flicked_wizcards, send_data=True):
        out = None
	own_wizcard = user.wizcard
        if flicked_wizcards:
	    #wizcards = map(lambda x: x.wizcard, flicked_wizcards)
            out = WizcardFlick.objects.serialize_split(user.wizcard, flicked_wizcards, send_data=send_data)
            self.add_data_with_notif(out, self.FLICKED_WIZCARD)
        return self.response

    def notifUserLookup(self, count, me, users, send_data=True):
        out = None
        if users:
            out = UserProfile.objects.serialize_split(me, users, 
                    send_data=send_data)
            self.add_data_with_notif(out, self.NEARBY_USERS)
        return self.response

    def notifTableLookup(self, count, user, tables):
        out = None
        if tables:
            out = VirtualTable.objects.serialize_split(tables, user)
            self.add_data_with_notif(out, self.NEARBY_TABLES)
        return self.response


