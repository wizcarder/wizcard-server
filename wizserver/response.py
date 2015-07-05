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

    def __init__(self, _err):
        self.errno = _err[errno]
        self.description = _err[str]


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

    def add_notif_type(self, d, _type):
        d['notifType'] = _type

    def add_data_with_notif(self, d, n):
        a = self.add_data_array(d)
        self.add_notif_type(a, n)

    def add_data_to_dict(self, _dict, k, v):
        _dict[k] = v


class NotifResponse(ResponseN):

    def __init__(self, notifications):
        ResponseN.__init__(self)
        notifHandler = {
            verbs.WIZREQ_U[0] 	                : self.notifWizConnectionU,
            verbs.WIZREQ_T[0]  	                : self.notifWizConnectionT,
            verbs.WIZCARD_ACCEPT[0]             : self.notifAcceptedWizcard,
            verbs.WIZCARD_REVOKE[0]	            : self.notifRevokedWizcard,
            verbs.WIZCARD_WITHDRAW_REQUEST[0]   : self.notifWithdrawRequest,
            verbs.WIZCARD_DELETE[0]	            : self.notifRevokedWizcard,
            verbs.WIZCARD_TABLE_TIMEOUT[0]      : self.notifDestroyedTable,
            verbs.WIZCARD_TABLE_DESTROY[0]      : self.notifDestroyedTable,
            verbs.WIZCARD_TABLE_JOIN[0]         : self.notifJoinTable,
            verbs.WIZCARD_TABLE_LEAVE[0]        : self.notifLeaveTable,
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
        wizcard = notif.target
        out = Wizcard.objects.serialize(wizcard,
                template=fields.wizcard_template_full)

        if notif.action_object and notif.action_object.cctx != '':
            cctx = notif.action_object.cctx
            nctx = NotifContext(cctx.description, cctx.asset_id, cctx.asset_type)

            if cctx.asset_type == ContentType.objects.get(model="virtualtable").name:
                #AA:TODO this lookup can be avoided by using the notify.send better
                #ie, no need to send target as wizcard since it can be derived from sender,recipient
                nctx.key_val('numSitting', VirtualTable.objects.get(id=cctx.asset_id).numSitting)
                #AA:TODO remove after app starts using context
                self.add_data_to_dict(
                        out,
                        "tableID",
                        nctx.id)
            elif cctx.asset_type == ContentType.objects.get(model="wizcardflick").name:
                self.add_data_to_dict(
                        out,
                        "flickCardID",
                        nctx.id)

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
        #AA:TODO we're using user id, but could actually used wizcardID
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

    def notifJoinTable(self, notif):
        wizcard=notif.actor.wizcard
        ws = wizcard.serialize(fields.wizcard_template_thumbnail_only)

        if notif.target: #since there is a possibility that the table got destroyed in-between
            out = dict(
                tableID=notif.target_object_id,
                numSitting=notif.target.numSitting,
                wizcard=ws
            )
            self.add_data_with_notif(out, verbs.TABLE_JOIN)
            logger.debug('%s', self.response)

        return self.response

    def notifLeaveTable(self, notif):
        wizcard=notif.actor.wizcard
        ws = wizcard.serialize(fields.wizcard_template_thumbnail_only)

        if notif.target:
            out = dict(
                tableID=notif.target_object_id,
                numSitting=notif.target.numSitting,
                wizcard=ws
            )
            self.add_data_with_notif(out, verbs.TABLE_LEAVE)
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
        out = dict(wizUserID=notif.actor_object_id, flickCardID=notif.target_object_id)
        self.add_data_with_notif(out, verbs.FLICK_PICK)
        logger.debug('%s', self.response)
        return self.response

    def notifWizcardTableInvite(self, notif):
        s_out = Wizcard.objects.serialize(notif.actor.wizcard,
                                          template=fields.wizcard_template_brief)
        a_out = VirtualTable.objects.serialize(notif.target,
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
                fields.nearby_table_template
            )
            self.add_data_with_notif(out, verbs.NEARBY_TABLES)
        return self.response