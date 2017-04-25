# define all outbound responses here
import datetime
from django.contrib.contenttypes.models import ContentType
from wizcardship.models import  Wizcard, WizcardFlick
from entity.models import VirtualTable
from userprofile.models import UserProfile
from base.cctx import NotifContext
from django.http import HttpResponse
#from wizcard.celery import client
from raven.contrib.django.raven_compat.models import client
import logging
import fields
import simplejson as json
import pdb
from wizserver import verbs

logger = logging.getLogger(__name__)

#This is the basic Response class used to send simple result and data
class Response:
    def __init__(self):
        self.response = dict(result=dict(Error=0, Description=""), data=dict())

    def __repr__(self):
        return "Sending Response" + json.dumps(self.response)

    def respond(self):
        ret = json.dumps(self.response) if self.response else None
        logger.debug('%s', self)
        return HttpResponse(ret)

    def add_result(self, k, v):
        self.response['result'][k] = v

    def add_data(self, k, v):
        self.response['data'][k] = v

    def error_response(self, err):
        self.add_result("Error", err['errno'])
        self.add_result("Description", err['str'])
        logger.error('%s: %s' % (err['errno'], err['str']))
        try:
            raise RuntimeError('%s: %s' % (err['errno'], err['str']))
        except:
            client.captureException()
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

    def add_seq(self, d, _s):
        d['notificationId'] = _s

    def add_data_and_seq_with_notif(self, d, n, seq=0):
        a = self.add_data_array(d)
        self.add_notif_type(a, n)
        if seq:
            self.add_seq(a, seq)
        return a

    def add_data_to_dict(self, _dict, k, v):
        _dict[k] = v

class NotifResponse(ResponseN):

    def __init__(self, notifications):
        ResponseN.__init__(self)
        notifHandler = {
            verbs.WIZREQ_U[0] 	                : self.notifWizConnectionU,
            verbs.WIZREQ_T[0]  	                : self.notifWizConnectionT,
            verbs.WIZREQ_T_HALF[0]              : self.notifWizConnectionH,
            verbs.WIZREQ_F[0]                   : self.notifWizConnectionF,
            verbs.WIZCARD_ACCEPT[0]             : self.notifAcceptedWizcard,
            verbs.WIZCARD_REVOKE[0]	            : self.notifRevokedWizcard,
            verbs.WIZCARD_WITHDRAW_REQUEST[0]   : self.notifWithdrawRequest,
            verbs.WIZCARD_DELETE[0]	            : self.notifRevokedWizcard,
            verbs.WIZCARD_TABLE_TIMEOUT[0]      : self.notifDestroyedTable,
            verbs.WIZCARD_TABLE_DESTROY[0]      : self.notifDestroyedTable,
            verbs.WIZCARD_TABLE_JOIN[0]         : self.notifJoinTable,
            verbs.WIZCARD_TABLE_LEAVE[0]        : self.notifLeaveTable,
            verbs.WIZCARD_UPDATE[0]             : self.notifWizcardUpdate,
            verbs.WIZCARD_UPDATE_HALF[0]        : self.notifWizcardUpdateH,
            verbs.WIZCARD_FLICK_TIMEOUT[0]      : self.notifWizcardFlickTimeout,
            verbs.WIZCARD_FLICK_PICK[0]         : self.notifWizcardFlickPick,
            verbs.WIZCARD_TABLE_INVITE[0]       : self.notifWizcardTableInvite,
            verbs.WIZCARD_FORWARD[0]            : self.notifWizcardForward,
            verbs.WIZWEB_WIZCARD_UPDATE[0]      : self.notifWizWebWizcardUpdate,
        }
        for notification in notifications:
            notifHandler[notification.verb](notification)

    def notifWizcard(self, notif, notifType, half=False):
        wizcard = notif.target
        template = fields.wizcard_template_half if half else fields.wizcard_template_full

        out = Wizcard.objects.serialize(wizcard,
                template=template)

        if notif.action_object and notif.action_object.cctx != '':
            cctx = notif.action_object.cctx

            #update the timestamp on the WizConnectionRequest
            notif.action_object.created = datetime.datetime.now()
            notif.action_object.save()

            nctx = NotifContext(
                description=cctx.description,
                asset_id=cctx.asset_id,
                asset_type=cctx.asset_type,
                connection_mode=cctx.connection_mode,
                timestamp = notif.action_object.created.strftime("%d. %B %Y")
            )

            if cctx.asset_type == ContentType.objects.get(model="virtualtable").name:
                #AA:TODO this lookup can be avoided by using the notify.send better
                #ie, no need to send target as wizcard since it can be derived from sender,recipient
                nctx.key_val('numSitting', VirtualTable.objects.get(id=cctx.asset_id).num_sitting)

            self.add_data_to_dict(out, "context", nctx.context)


        self.add_data_and_seq_with_notif(out, notifType, notif.id)

        return self.response

    def notifWizConnectionT(self, notif):
        return self.notifWizcard(notif, verbs.NOTIF_ACCEPT_IMPLICIT)

    def notifWizConnectionH(self, notif):
        return self.notifWizcard(notif, verbs.NOTIF_ACCEPT_IMPLICIT, half=True)

    def notifWizConnectionU(self, notif):
        # clear the acted flag. This will get set back when app tells us
        # via accept/decline_connection req
        notif.set_acted(False)
        return self.notifWizcard(notif, verbs.NOTIF_ACCEPT_EXPLICIT)

    def notifWizConnectionF(self, notif):
        return self.notifWizcard(notif, verbs.NOTIF_FOLLOW_EXPLICIT)

    def notifAcceptedWizcard(self, notif):
        out = dict(wizCardID=notif.target_object_id)
        self.add_data_and_seq_with_notif(out, verbs.NOTIF_WIZCARD_ACCEPT, notif.id)
        return self.response

    def notifRevokedWizcard(self, notif):
        #this is a notif to the app B when app A removed B's card
        #AA:TODO we're using user id, but could actually used wizcardID
        out = dict(user_id=notif.actor_object_id)
        self.add_data_and_seq_with_notif(out, verbs.NOTIF_DELETE_IMPLICIT, notif.id)
        return self.response

    def notifWithdrawRequest(self, notif):
        #this is a notif to the app B when app A withdraws it's connection request
        out = dict(user_id=notif.actor_object_id)
        self.add_data_and_seq_with_notif(out, verbs.NOTIF_WITHDRAW_REQUEST, notif.id)
        logger.debug('%s', self.response)
        return self.response

    def notifDestroyedTable(self, notif):
        out = dict(tableID=notif.target_object_id)
        self.add_data_and_seq_with_notif(out, verbs.NOTIF_TABLE_TIMEOUT, notif.id)
        logger.debug('%s', self.response)
        return self.response

    def notifJoinTable(self, notif):
        wizcard=notif.actor.wizcard
        ws = wizcard.serialize(fields.wizcard_template_thumbnail_only)

        if notif.target: #since there is a possibility that the table got destroyed in-between
            out = dict(
                tableID=notif.target_object_id,
                numSitting=notif.target.num_sitting,
                wizcard=ws
            )
            self.add_data_and_seq_with_notif(out, verbs.NOTIF_TABLE_JOIN, notif.id)
            logger.debug('%s', self.response)

        return self.response

    def notifLeaveTable(self, notif):
        wizcard=notif.actor.wizcard
        ws = wizcard.serialize(fields.wizcard_template_thumbnail_only)

        if notif.target:
            out = dict(
                tableID=notif.target_object_id,
                numSitting=notif.target.num_sitting,
                wizcard=ws
            )
            self.add_data_and_seq_with_notif(out, verbs.NOTIF_TABLE_LEAVE, notif.id)
            logger.debug('%s', self.response)
        return self.response

    def notifWizcardUpdate(self, notif):
        return self.notifWizcard(notif, verbs.NOTIF_UPDATE_WIZCARD)

    def notifWizcardUpdateH(self, notif):
        return self.notifWizcard(notif, verbs.NOTIF_UPDATE_WIZCARD, half=True)

    def notifWizWebWizcardUpdate(self, notif):
        return self.notifWizcard(notif, verbs.NOTIF_WIZWEB_UPDATE_WIZCARD)

    def notifWizcardFlickTimeout(self, notif):
        out = dict(flickCardID=notif.target_object_id)
        self.add_data_and_seq_with_notif(out, verbs.NOTIF_FLICK_TIMEOUT, notif.id)
        logger.debug('%s', self.response)
        return self.response

    def notifWizcardFlickPick(self, notif):
        out = dict(wizCardID=notif.actor.wizcard.id, flickCardID=notif.target_object_id)
        self.add_data_and_seq_with_notif(out, verbs.NOTIF_FLICK_PICK, notif.id)
        logger.debug('%s', self.response)
        return self.response

    def notifWizcardTableInvite(self, notif):
        s_out = Wizcard.objects.serialize(notif.actor.wizcard,
                                          template=fields.wizcard_template_brief)
        a_out = VirtualTable.objects.serialize(notif.target,
                                               template=fields.nearby_table_template)

        out = dict(sender=s_out, asset=a_out)
        self.add_data_and_seq_with_notif(out, verbs.NOTIF_TABLE_INVITE, notif.id)
        return self.response

    def notifWizcardForward(self, notif):
        return self.response

    def notifFlickedWizcardsLookup(self, count, user, flicked_wizcards):
        out = None
        own_wizcard = user.wizcard
        if flicked_wizcards:
            out = WizcardFlick.objects.serialize_split(user.wizcard,
                                                       flicked_wizcards)
            self.add_data_and_seq_with_notif(out, verbs.NOTIF_NEARBY_FLICKED_WIZCARD)
        return self.response

    def notifUserLookup(self, count, me, users):
        out = None
        if users:
            out = UserProfile.objects.serialize_split(me, users)
            self.add_data_and_seq_with_notif(out, verbs.NOTIF_NEARBY_USERS)
        return self.response

    def notifTableLookup(self, count, user, tables):
        out = None
        if tables:
            out = VirtualTable.objects.serialize_split(
                tables,
                user,
                fields.nearby_table_template
            )
            self.add_data_and_seq_with_notif(out, verbs.NOTIF_NEARBY_TABLES)
        return self.response
