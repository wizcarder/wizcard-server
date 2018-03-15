# define all outbound responses here
from django.contrib.contenttypes.models import ContentType
from wizcardship.models import Wizcard
from entity.models import VirtualTable
from base.cctx import NotifContext
from django.http import HttpResponse
from raven.contrib.django.raven_compat.models import client
import logging
import simplejson as json
import pdb
from wizserver import verbs
from entity.serializers import EntitySerializerL0
from wizcardship.serializers import WizcardSerializerL1, WizcardSerializerL2
from entity.serializers import TableSerializerL1
from django.utils import timezone
from django.conf import settings
from notifications.signals import notify
from notifications.push_tasks import push_notification_to_app
from lib.create_share import send_event, send_wizcard
from notifications.serializers import SyncNotificationSerializer

logger = logging.getLogger(__name__)


# This is the basic Response class used to send simple result and data
class Response:
    def __init__(self):
        self.response = dict(result=dict(Error=0, Description=""), data=dict())

    def __repr__(self):
        return "Sending Response" + json.dumps(self.response, indent=4)

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
            if hasattr(settings, 'RAVEN_CONFIG'):
                client.captureException()
            else:
                pass
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

class SyncNotifResponse(ResponseN):

    def __init__(self, notifications):
        ResponseN.__init__(self)
        notif_handler = {
            verbs.get_notif_type(verbs.WIZREQ_U)                    : self.notifWizcard,
            verbs.get_notif_type(verbs.WIZREQ_T)  	                : self.notifWizcard,
            verbs.get_notif_type(verbs.WIZREQ_T_HALF)               : self.notifWizcard,
            verbs.get_notif_type(verbs.WIZCARD_UPDATE_FULL)         : self.notifWizcard,
            verbs.get_notif_type(verbs.WIZCARD_UPDATE_HALF)         : self.notifWizcard,
            verbs.get_notif_type(verbs.WIZCARD_REVOKE)	            : self.notifRevokedWizcard,
            verbs.get_notif_type(verbs.WIZCARD_WITHDRAW_REQUEST)    : self.notifWithdrawRequest,
            verbs.get_notif_type(verbs.WIZCARD_DELETE)	            : self.notifRevokedWizcard,
            verbs.get_notif_type(verbs.WIZCARD_FLICK_TIMEOUT)       : self.notifWizcardFlickTimeout,
            verbs.get_notif_type(verbs.WIZCARD_FLICK_PICK)          : self.notifWizcardFlickPick,
            verbs.get_notif_type(verbs.WIZCARD_TABLE_INVITE)        : self.notifWizcardTableInvite,
            verbs.get_notif_type(verbs.WIZCARD_ENTITY_ATTACH)       : self.notifJoinEntity,
            verbs.get_notif_type(verbs.WIZCARD_ENTITY_DETACH)       : self.notifLeaveEntity,
            verbs.get_notif_type(verbs.WIZCARD_ENTITY_UPDATE)       : self.notifEntity,
            verbs.get_notif_type(verbs.WIZCARD_ENTITY_EXPIRE)       : self.notifEntity,
            verbs.get_notif_type(verbs.WIZCARD_ENTITY_DELETE)       : self.notifEntity,
            verbs.get_notif_type(verbs.WIZCARD_ENTITY_BROADCAST)    : self.notifEntityBroadcast,
        }

        for notification in notifications:
            notif_handler[notification.notif_type](notification)

    def notifWizcard(self, notif):
        wizcard = notif.target
        r_wizcard = notif.recipient.wizcard

        s = WizcardSerializerL1 if notif.notif_type in [verbs.NOTIF_ACCEPT_IMPLICIT_H, verbs.NOTIF_UPDATE_WIZCARD_H] \
            else WizcardSerializerL2

        if notif.notif_type == verbs.NOTIF_ACCEPT_EXPLICIT:
            # clear the acted flag. This will get set back when app tells us
            # via accept/decline_connection req
            notif.set_acted(False)

        user_state = Wizcard.objects.get_connection_status(r_wizcard, wizcard)

        out = s(wizcard, context={'user_state': user_state}).data

        if notif.action_object and notif.action_object.cctx != '':
            cctx = notif.action_object.cctx

            # update the timestamp on the WizConnectionRequest
            notif.action_object.created = timezone.now()
            notif.action_object.save()

            nctx = NotifContext(
                description=cctx.description,
                asset_id=cctx.asset_id,
                asset_type=cctx.asset_type,
                connection_mode=cctx.connection_mode,
                timestamp=notif.action_object.created.strftime("%d. %B %Y")
            )

            if cctx.asset_type == ContentType.objects.get(model="virtualtable").name:
                entity = VirtualTable.objects.get(id=cctx.asset_id)
                entity_s = EntitySerializerL0(entity).data
                nctx.key_val('entity', entity_s)

            self.add_data_to_dict(out, "context", nctx.context)

        self.add_data_and_seq_with_notif(out, notif.notif_type, notif.id)

        return self.response

    def notifRevokedWizcard(self, notif):
        #this is a notif to the app B when app A removed B's card
        out = dict(wizcard_id=notif.target_object_id)
        self.add_data_and_seq_with_notif(out, verbs.NOTIF_DELETE_IMPLICIT, notif.id)
        return self.response

    def notifWithdrawRequest(self, notif):
        #this is a notif to the app B when app A withdraws it's connection request
        out = dict(wizcard_id=notif.target_object_id)
        self.add_data_and_seq_with_notif(out, verbs.NOTIF_WITHDRAW_REQUEST, notif.id)
        return self.response

    def notifJoinEntity(self, notif):
        wizcard=notif.action_object.wizcard
        ws = WizcardSerializerL1(wizcard, context={'user': notif.recipient}).data

        # since there is a possibility that the entity got destroyed in-between
        if notif.target:
            s = EntitySerializerL0(notif.target).data
            out = dict(
                entity=s,
                wizcard=ws
            )
            self.add_data_and_seq_with_notif(out, verbs.NOTIF_ENTITY_ATTACH, notif.id)

        return self.response

    def notifLeaveEntity(self, notif):
        wizcard = notif.action_object.wizcard
        ws = WizcardSerializerL1(wizcard).data

        s = EntitySerializerL0(notif.target).data

        out = dict(
            entity=s,
            wizcard=ws
        )

        self.add_data_and_seq_with_notif(out, verbs.NOTIF_ENTITY_DETACH, notif.id)

        return self.response

    def notifEntityBroadcast(self, notif):
        out = SyncNotificationSerializer(notif).data
        self.add_data_and_seq_with_notif(out, notif.notif_type, notif.id)

        return self.response

    def notifEntity(self, notif):
        out = notif.build_response_dict()
        self.add_data_and_seq_with_notif(out, notif.notif_type, notif.id)

        return self.response

    def notifWizcardFlickTimeout(self, notif):
        out = dict(flickCardID=notif.target_object_id)
        self.add_data_and_seq_with_notif(out, verbs.NOTIF_FLICK_TIMEOUT, notif.id)
        return self.response

    def notifWizcardFlickPick(self, notif):
        out = dict(wizCardID=notif.actor.wizcard.id, flickCardID=notif.target_object_id)
        self.add_data_and_seq_with_notif(out, verbs.NOTIF_FLICK_PICK, notif.id)
        return self.response

    def notifWizcardTableInvite(self, notif):
        s_out = WizcardSerializerL1(notif.actor.wizcard, context={'user': notif.recipient}).data
        a_out = TableSerializerL1(notif.target, context={'user': notif.recipient}).data

        out = dict(sender=s_out, asset=a_out)
        self.add_data_and_seq_with_notif(out, verbs.NOTIF_TABLE_INVITE, notif.id)
        return self.response
    #
    # def notifFlickedWizcardsLookup(self, count, user, flicked_wizcards):
    #     out = None
    #     own_wizcard = user.wizcard
    #     if flicked_wizcards:
    #         out = WizcardFlick.objects.serialize_split(user.wizcard,
    #                                                    flicked_wizcards)
    #         self.add_data_and_seq_with_notif(out, verbs.NOTIF_NEARBY_FLICKED_WIZCARD)
    #     return self.response

    def notifUserLookup(self, me, users):
        wizcards = map(lambda u: u.wizcard, users)
        out = WizcardSerializerL1(wizcards, many=True, context={'user': me}).data
        self.add_data_and_seq_with_notif(out, verbs.NOTIF_NEARBY_USERS)

        return self.response

    def notifTableLookup(self,  user, tables):
        out = TableSerializerL1(tables, many=True, context={'user': user}).data
        self.add_data_and_seq_with_notif(out, verbs.NOTIF_NEARBY_TABLES)

        return self.response


class AsyncNotifResponse:
    def __init__(self, notifications):
        notifHandler = {
            verbs.get_notif_type(verbs.WIZCARD_EVENT_REMINDER)      : self.notifEventReminder,
            verbs.get_notif_type(verbs.WIZCARD_NEW_USER)            : self.notifNewUser,
            verbs.get_notif_type(verbs.WIZCARD_SCANNED_USER)        : self.notifScannedUser,
            verbs.get_notif_type(verbs.WIZCARD_INVITE_USER)         : self.notifInviteUser,
            verbs.get_notif_type(verbs.WIZCARD_INVITE_EXHIBITOR)    : self.notifInviteExhibitor,
            verbs.get_notif_type(verbs.WIZCARD_INVITE_ATTENDEE)     : self.notifInviteAttendee,
            verbs.get_notif_type(verbs.WIZCARD_ENTITY_BROADCAST)    : self.notif_async_2_sync,
            verbs.get_notif_type(verbs.WIZCARD_ENTITY_DELETE)       : self.notif_async_2_sync,
            verbs.get_notif_type(verbs.WIZCARD_UPDATE_HALF)         : self.notif_async_2_sync,
            verbs.get_notif_type(verbs.WIZCARD_UPDATE_FULL)         : self.notif_async_2_sync,
            verbs.get_notif_type(verbs.WIZCARD_ENTITY_ATTACH)       : self.notif_async_2_sync,
            verbs.get_notif_type(verbs.WIZCARD_ENTITY_DETACH)       : self.notif_async_2_sync,
            verbs.get_notif_type(verbs.WIZCARD_ENTITY_UPDATE)       : self.notif_async_2_sync,
            verbs.get_notif_type(verbs.WIZCARD_ENTITY_EXPIRE)       : self.notif_async_2_sync,
            verbs.get_notif_type(verbs.WIZCARD_ENTITY_DELETE)       : self.notif_async_2_sync
        }

        for notification in notifications:
            # AA: TODO: IMPORTANT: before prod, put a try except here and raise
            # any errors so that the loop is not interrupted by some bug in a
            # particular notif handling.
            notifHandler[notification.notif_type](notification)

    def notif_async_2_sync(self, notif):
        target_ct = notif.target_content_type
        # AA: TODO: this might have been expired/deleted in the meantime
        entity = target_ct.get_object_for_this_type(id=notif.target_object_id)
        ntuple = verbs.notif_type_tuple_dict[notif.notif_type]

        # get the flood set for this target
        flood_set = entity.flood_set(ntuple=ntuple, sender=notif.actor)
        if not flood_set:
            return

        # Q sync notif for each in flood_set
        for recipient in flood_set:
            notify.send(
                notif.actor,
                recipient=recipient,
                notif_tuple=ntuple,
                target=notif.target,
                action_object=notif.action_object,
                notif_operation=notif.notif_operation,
                notification_text=notif.notification_text,
                verb=notif.verb,
                # tell signal handler explicitly to Q into SyncQ and not use notif_type to decide
                force_sync=True,
                # no need to double-push. We'll send bulk push from here itself
                do_push=False
            )

        # bulk push
        if verbs.get_notif_apns_required(ntuple):
            push_notification_to_app.delay(notif, ntuple, flood_set)

    def notifEventReminder(self, notif):
        pass

    def notifNewUser(self, notif):
        wizcard = notif.target
        to = notif.target.get_email
        email_details = verbs.EMAIL_TEMPLATE_MAPPINGS[notif.notif_type]
        send_wizcard(wizcard, to, email_details, half_card=True)

        return 0

    def notifScannedUser(self, notif):
        wizcard = notif.actor.wizcard
        to = notif.target.get_email
        email_details = verbs.EMAIL_TEMPLATE_MAPPINGS[notif.notif_type]
        send_wizcard(wizcard, to, email_details, half_card=True)

    def notifInviteUser(self, notif):
        wizcard = notif.actor.wizcard
        to = notif.target.email
        email_details = verbs.EMAIL_TEMPLATE_MAPPINGS[notif.notif_type]
        send_wizcard(wizcard, to, email_details)

    def notifInviteExhibitor(self, notif):
        event_organizer = notif.actor
        email_details = verbs.EMAIL_TEMPLATE_MAPPINGS[notif.notif_type]
        send_event(event_organizer, notif.recipient, email_details)

    def notifInviteAttendee(self, notif):
        event_organizer = notif.actor
        email_details = verbs.EMAIL_TEMPLATE_MAPPINGS[notif.notif_type]
        send_event(event_organizer, notif.recipient, email_details)


