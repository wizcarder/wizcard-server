# define all outbound responses here
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from wizcardship.models import WizConnectionRequest, Wizcard, WizcardFlick
from virtual_table.models import VirtualTable
from userprofile.models import UserProfile
from notifications.models import Notification
from base.cctx import NotifContext
from django.http import HttpResponse
import logging
import fields
import json
import pdb
from wizcard import err
from wizserver import verbs

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

    def __init__(self, notifications):
        ResponseN.__init__(self)
        notifHandler = {
            verbs.WIZREQ_U[0] 	                : self.notifWizConnectionU,
            verbs.WIZREQ_T[0]  	                : self.notifWizConnectionT,
            verbs.WIZCARD_ACCEPT[0]             : self.notifAcceptedWizcard,
            verbs.WIZCARD_REVOKE[0]	        : self.notifRevokedWizcard,
            verbs.WIZCARD_WITHDRAW_REQUEST[0]   : self.notifWithdrawRequest,
            verbs.WIZCARD_DELETE[0]	        : self.notifRevokedWizcard,
            verbs.WIZCARD_TABLE_TIMEOUT[0]      : self.notifDestroyedTable,
            verbs.WIZCARD_TABLE_DESTROY[0]      : self.notifDestroyedTable,
            verbs.WIZCARD_UPDATE[0]             : self.notifWizcardUpdate,
            verbs.WIZCARD_FLICK_TIMEOUT[0]      : self.notifWizcardFlickTimeout,
            verbs.WIZCARD_FLICK_PICK[0]         : self.notifWizcardFlickPick,
            verbs.WIZCARD_TABLE_INVITE[0]       : self.notifWizcardTableInvite,
            verbs.WIZCARD_FORWARD[0]            : self.notifWizcardForward,
            verbs.WIZWEB_WIZCARD_UPDATE[0]      : self.notifWizWebWizcardUpdate
        }
	for notification in notifications:
	    notifHandler[notification.verb](notification)

    def notifWizcard(self, notif, notifType):
        wizcard = Wizcard.objects.get(id=notif.target_object_id)
        out = Wizcard.objects.serialize(wizcard, template=fields.wizcard_template_full)

	if notif.action_object:
            if ContentType.objects.get_for_model(notif.action_object) == \
                    ContentType.objects.get(model="wizcardflick"):
                    self.add_data_to_dict(out, "flickCardID",
                            notif.action_object_object_id)
            elif ContentType.objects.get_for_model(notif.action_object) == \
                    ContentType.objects.get(model="virtualtable"):
                    self.add_data_to_dict(out, "tableID",
                            notif.action_object_object_id)
                    try:
                        num_sitting = \
                                VirtualTable.objects.get\
                                (id=notif.action_object_object_id).numSitting
                    except:
                        num_sitting = 0
                    self.add_data_to_dict(out, "numSitting", num_sitting)

            nctx = NotifContext(
                    notif.action_object_object_id,
                    ContentType.objects.get_for_model(
                        notif.action_object).name,
                    notif.description)
            self.add_data_to_dict(out, "context", nctx.context)

        self.add_data_with_notif(out, notifType)
        return self.response

    def notifWizConnectionT(self, notif):
        return self.notifWizcard(notif, verbs.ACCEPT_IMPLICIT)

    def notifWizConnectionU(self, notif):
        return self.notifWizcard(notif, verbs.ACCEPT_EXPLICIT)

    def notifAcceptedWizcard(self, notif):
        return self.notifWizConnectionT(notif)

    def notifRevokedWizcard(self, notif):
        #this is a notif to the app B when app A removed B's card
        out = dict(user_id=notif.actor_object_id)
        self.add_data_with_notif(out, verbs.DELETE_IMPLICIT)
        return self.response

    def notifWithdrawRequest(self, notif):
        #this is a notif to the app B when app A withdraws it's connection request
        out = dict(user_id=notif.actor_object_id)
        self.add_data_with_notif(out, verbs.WITHDRAW_REQUEST)
        logger.debug('%s', self.response)
        return self.response

    def notifDestroyedTable(self, notif):
        out = dict(tableID=notif.target_object_id)
        self.add_data_with_notif(out, verbs.TABLE_TIMEOUT)
        logger.debug('%s', self.response)
        return self.response

    def notifWizcardUpdate(self, notif):
        return self.notifWizcard(notif, verbs.UPDATE_WIZCARD)

    def notifWizWebWizcardUpdate(self, notif):
        return self.notifWizcard(notif, verbs.WIZWEB_UPDATE_WIZCARD)

    def notifWizcardFlickTimeout(self, notif):
	out = dict(flickCardID=notif.target_object_id)
        self.add_data_with_notif(out, verbs.FLICK_TIMEOUT)
        logger.debug('%s', self.response)
        return self.response

    def notifWizcardFlickPick(self, notif):
        out = dict(wizUserID=notif.action_object_object_id, flickCardID=notif.target_object_id)
        self.add_data_with_notif(out, verbs.FLICK_PICK)
        logger.debug('%s', self.response)
        return self.response

    def notifWizcardTableInvite(self, notif):
        sender = User.objects.get(id=notif.action_object_object_id)
        table = VirtualTable.objects.get(id=notif.target_object_id)
        s_out = Wizcard.objects.serialize(sender.wizcard,
                template=fields.wizcard_template_brief)
        a_out = VirtualTable.objects.serialize(table,
                template=fields.nearby_table_template)

        out = dict(sender=s_out, asset=a_out)
        self.add_data_with_notif(out, verbs.TABLE_INVITE)
        return self.response

    def notifWizcardForward(self, notif):
        return self.response

    def notifFlickedWizcardsLookup(self, count, user, flicked_wizcards):
        out = None
	own_wizcard = user.wizcard
        if flicked_wizcards:
	    #wizcards = map(lambda x: x.wizcard, flicked_wizcards)
            out = WizcardFlick.objects.serialize_split(user.wizcard,
                                                       flicked_wizcards)
            self.add_data_with_notif(out, verbs.NEARBY_FLICKED_WIZCARD)
        return self.response

    def notifUserLookup(self, count, me, users):
        out = None
        if users:
            out = UserProfile.objects.serialize_split(me, users)
            self.add_data_with_notif(out, verbs.NEARBY_USERS)
        return self.response

    def notifTableLookup(self, count, user, tables):
        out = None
        if tables:
            out = VirtualTable.objects.serialize_split(
                    tables,
                    user,
                    fields.nearby_table_template)
            self.add_data_with_notif(out, verbs.NEARBY_TABLES)
        return self.response


