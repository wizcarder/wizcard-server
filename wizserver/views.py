""" .. autofunction:: wizconnection_request

.. autofunction:: wizconnection_accept

.. autofunction:: wizconnection_decline

.. autofunction:: wizconnection_cancel

.. autofunction:: wizconnection_delete

.. autofunction:: user_block

.. autofunction:: user_unblock
"""
import json
import logging
import re
import random

from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
import colander
from converter import Converter

from lib.ocr import OCR
from wizcardship.models import  Wizcard, DeadCard, ContactContainer, WizcardFlick
from notifications.models import notify, Notification
from entity.models import VirtualTable
from meishi.models import Meishi
from response import Response, NotifResponse
from userprofile.models import UserProfile
from userprofile.models import FutureUser
from lib import wizlib, noembed
from lib.create_share import create_vcard
from email_and_push_infra.models import EmailEvent
from email_and_push_infra.signals import email_trigger
from wizcard import err
from base_entity.models import BaseEntity
from entity.models import Event
from wizserver import fields
from lib.nexmomessage import NexmoMessage
from wizcard import message_format as message_format
from wizserver import verbs
from base.cctx import ConnectionContext
from recommendation.models import UserRecommendation, genreco
from wizserver.tasks import contacts_upload_task
from stats.models import Stats
from entity.serializers import EventSerializerL1
from base_entity.serializers import  EntityEngagementSerializer
from wizcardship.serializers import WizcardSerializerL1, WizcardSerializerL2, DeadCardSerializerL2
from userprofile.serializers import UserSerializerL0
from base_entity.models import EntityUserStats
from base_entity.models import BaseEntityComponent
from media_components.models import MediaEntities
from media_components.signals import media_create

import pdb

now = timezone.now

logger = logging.getLogger(__name__)

class WizRequestHandler(View):
    def post(self, request, *args, **kwargs):
        self.request = request
        logger.debug(request)

        # Dispatch to appropriate message handler
        pdispatch = ParseMsgAndDispatch(self.request)
        #try:
        pdispatch.dispatch()
        #except:
        #    client.captureException()
        #    pdispatch.response.error_response(err.INTERNAL_ERROR)
        #send response
        return pdispatch.response.respond()

class ParseMsgAndDispatch(object):
    def __init__(self, request):
        self.request = request
        self.response = Response
        self.msg = (json.loads(self.request.body)).copy()
        self.msg_type = None
        self.device_id = None
        self.password_hash = None
        self.user = None
        self.userprofile = None
        self.sender = None
        self.receiver = None
        self.response = Response()
        self.user_stats = None
        self.global_stats = Stats.objects.get_global_stat()

    def __repr__(self):
        out = ""
        if self.msg.has_key('header'):
            out += str(self.msg['header'])
        if self.msg.has_key('sender'):
            out += str(self.msg['sender'])
        if self.msg.has_key('receiver'):
            out += str(self.msg['receiver'])
        return out

    def dispatch(self):
        status, response =  self.validate()
        if not status:
            return response

        return self.header_process()

    def security_exception(self):
        #AA TODO
        return None

    # note: this assumes that self.msg is stored in self without any changes
    def msg_has_location(self):
        return ('lat' in self.msg['header'] and 'lng' in self.msg['header']) or ('lat' in self.msg['sender'] and 'lng' in self.msg['sender'])

    def msg_is_initial(self):
        return self.msg_type in ['phone_check_req', 'phone_check_rsp', 'login']

    def msg_has_rawimage(self):
        return self.msg_type in ['ocr_req_self', 'ocr_req_dead_card']

    def validate_header(self):
        #hashed passwd check
        #username, userID, wizuser_id, device_id
        #is_authenticated check
        if self.msg_type not in verbs.wizcardMsgTypes:
            return False

        self.msg_id = verbs.wizcardMsgTypes[self.msg_type]
        return True

    def validate_sender(self, sender):
        self.sender = sender
        if not self.msg_is_initial():
            wizuser_id = self.sender.pop('wizuser_id')
            user_id = self.sender.pop('user_id')
            try:
                self.user = User.objects.get(id=wizuser_id)
                self.userprofile = self.user.profile
                self.app_userprofile = self.user.profile.app_user()
                self.app_settings = self.app_userprofile.settings
                self.user_stats, created = Stats.objects.get_or_create(user=self.user)

                # used often by serializer. might as well put it here
                self.user_context = {'context': {'user': self.user}}
            except:
                logger.error('Failed User wizuser_id %s, user_id %s', wizuser_id, user_id)
                return False

            if str(self.userprofile.userid) != user_id:
                logger.error('Failed User wizuser_id %s, user_id %s', wizuser_id, user_id)
                return False

        #AA:TODO - Move to header
        if self.msg_has_location():
            self.lat = float(self.sender.pop('lat'))
            self.lng = float(self.sender.pop('lng'))
            logger.debug('User %s @lat, lng: {%s, %s}',
                         self.user.first_name+" "+self.user.last_name, self.lat, self.lng)

        return True

    def validate_app_version(self):
        if 'version' in self.msg['header']:
            appversion = self.msg['header']['version']
            versions = re.match('(\d+)\.(\d+)\.?(\d+)?', appversion)

            if versions:
                appmajor = int(versions.group(1))
                appminor = int(versions.group(2))

                # Checking major and minor versions only, expecting patches to be backward compatible
                # apppatch = int(versions.group(3))

                # Hack for earlier versions - AnandR to do version check as handlers and add default handler
                if appmajor == 1 and appminor >= 1:
                    if appminor <= 3:
                        return True

                if appmajor < settings.APP_MAJOR or (appmajor == settings.APP_MAJOR and appminor < settings.APP_MINOR):
                    logger.error('Failed Version Validation - App Version: %s , Expected Version - %s.%s', appversion, int(settings.APP_MAJOR), int(settings.APP_MINOR))
                    return False
                else:
                    return True
            else:
                logger.error('Not able to get Version from the client headers - Something Fishy')

        else:
            logger.error('Client not sending App Version - Something Fishy')
            return False

    def validate(self):
        try:
            #self.header = message_format.CommonHeaderSchema().deserialize(self.msg['header'])
            self.header = self.msg['header']
        except colander.Invalid:
            self.response.ignore()
            return False, self.response

        self.msg_type = self.header['msg_type']
        self.device_id = self.header['device_id']

        logger.debug('received message %s', self.msg_type)
        if not self.msg_has_rawimage():
            logger.debug('%s', self)

        if not self.validate_header():
            self.security_exception()
            self.response.ignore()
            logger.warning('user failed header security check on msg {%s}',
                           self.msg_type)
            return False, self.response

        if not self.validate_app_version():
            self.response.error_response(err.VERSION_UPGRADE)
            return False, self.response

        if self.msg.has_key('sender') and not self.validate_sender(self.msg['sender']):
            self.security_exception()
            self.response.ignore()
            logger.warning('user failed sender security check on msg {%s}',
                           self.msg_type)
            return False, self.response
        if 'receiver' in self.msg:
            self.receiver = self.msg['receiver']

        #AA:TODO: App to fix - This has to be in header
        self.on_wifi = self.sender['onWifi'] if \
            self.sender.has_key('onWifi') else False

        return True, self.response

    def header_process(self):
        VALIDATOR = 0
        HANDLER = 1
        STATS = 2

        msgTypesValidatorsAndHandlers = {
            # wizweb messages
            verbs.MSG_LOGIN:
                (
                    message_format.LoginSchema,
                    self.Login,
                    Stats.objects.inc_login
                ),
            verbs.MSG_PHONE_CHECK_REQ:
                (
                    message_format.PhoneCheckRequestSchema,
                    self.PhoneCheckRequest,
                    Stats.objects.inc_phone_check_req
                ),
            verbs.MSG_PHONE_CHECK_RESP:
                (
                    message_format.PhoneCheckResponseSchema,
                    self.PhoneCheckResponse,
                    Stats.objects.inc_phone_check_rsp
                ),
            verbs.MSG_REGISTER:
                (
                    message_format.RegisterSchema,
                    self.Register,
                    Stats.objects.inc_register
                 ),
            verbs.MSG_CURRENT_LOCATION:
                (
                    message_format.LocationUpdateSchema,
                    self.LocationUpdate,
                    Stats.objects.inc_location_update
                ),
            verbs.MSG_CONTACTS_UPLOAD:
                (
                    message_format.ContactsUploadSchema,
                    self.ContactsUpload,
                    Stats.objects.inc_contacts_upload
                ),
            verbs.MSG_NOTIFICATIONS_GET:
                (
                    message_format.NotificationsGetSchema,
                    self.NotificationsGet,
                    Stats.objects.inc_get_cards,
                ),
            verbs.MSG_WIZCARD_EDIT:
                (
                    message_format.WizcardEditSchema,
                    self.WizcardEdit,
                    Stats.objects.inc_edit_card,
                ),
            verbs.MSG_WIZCARD_ACCEPT:
                (
                    message_format.WizcardAcceptSchema,
                    self.WizcardAccept,
                    Stats.objects.inc_wizcard_accept,
                ),
            verbs.MSG_WIZCARD_DECLINE:
                (
                    message_format.WizConnectionRequestDeclineSchema,
                    self.WizConnectionRequestDecline,
                    Stats.objects.inc_wizcard_decline,
                ),
            verbs.MSG_ROLODEX_EDIT:
                (
                    message_format.RolodexEditSchema,
                    self.RolodexEdit,
                    Stats.objects.inc_rolodex_edit,
                ),
            verbs.MSG_ROLODEX_DELETE:
                (
                    message_format.WizcardRolodexDeleteSchema,
                    self.WizcardRolodexDelete,
                    Stats.objects.inc_rolodex_delete,
                ),
            verbs.MSG_ARCHIVED_CARDS:
                (
                    message_format.WizcardRolodexArchivedCardsSchema,
                    self.WizcardRolodexArchivedCards,
                    Stats.objects.inc_archived_cards,
                ),
            verbs.MSG_FLICK:
                (
                    message_format.WizcardFlickSchema,
                    self.WizcardFlick,
                    None,
                ),
            verbs.MSG_FLICK_ACCEPT:
                (
                    message_format.WizcardFlickPickSchema,
                    self.WizcardFlickPick,
                    None
                ),
            verbs.MSG_FLICK_ACCEPT_CONNECT:
                (
                    message_format.WizcardFlickConnectSchema,
                    self.WizcardFlickConnect,
                    None
                ),
            verbs.MSG_MY_FLICKS:
                (
                    message_format.WizcardMyFlickSchema,
                    self.WizcardMyFlicks,
                    None
                ),
            verbs.MSG_FLICK_WITHDRAW:
                (
                    message_format.WizcardFlickWithdrawSchema,
                    self.WizcardFlickWithdraw,
                    None
                ),
            verbs.MSG_FLICK_EDIT:
                (
                    message_format.WizcardFlickEditSchema,
                    self.WizcardFlickEdit,
                    None
                ),
            verbs.MSG_FLICK_QUERY:
                (
                    message_format.WizcardFlickQuerySchema,
                    self.WizcardFlickQuery,
                    None
                ),
            verbs.MSG_FLICK_PICKS:
                (
                    message_format.WizcardFlickPickersSchema,
                    self.WizcardFlickPickers,
                    None
                ),
            verbs.MSG_SEND_ASSET_XYZ:
                (
                    message_format.WizcardSendAssetToXYZSchema,
                    self.WizcardSendAssetToXYZ,
                    Stats.objects.inc_send_asset_xyz,
                ),
            verbs.MSG_QUERY_USER:
                (
                    message_format.UserQuerySchema,
                    self.UserQuery,
                    Stats.objects.inc_user_query,
                ),
            verbs.MSG_CARD_DETAILS:
                (
                    message_format.WizcardGetDetailSchema,
                    self.WizcardGetDetail,
                    Stats.objects.inc_card_details,
                ),
            verbs.MSG_SETTINGS:
                (
                    message_format.SettingsSchema,
                    self.Settings,
                    Stats.objects.inc_settings,
                ),
            verbs.MSG_OCR_SELF:
                (
                    message_format.OcrRequestSelfSchema,
                    self.OcrReqSelf,
                    Stats.objects.inc_ocr_self,
                ),
            verbs.MSG_OCR_DEAD_CARD:
                (
                    message_format.OcrRequestDeadCardSchema,
                    self.OcrReqDeadCard,
                    Stats.objects.inc_ocr_dead
                ),
            verbs.MSG_OCR_EDIT:
                (
                    message_format.OcrDeadCardEditSchema,
                    self.OcrDeadCardEdit,
                    Stats.objects.inc_ocr_dead_edit
                ),
            verbs.MSG_MEISHI_START:
                (
                    message_format.MeishiStartSchema,
                    self.MeishiStart,
                    None
                ),
            verbs.MSG_MEISHI_FIND:
                (
                    message_format.MeishiFindSchema,
                    self.MeishiFind,
                    None,
                ),
            verbs.MSG_MEISHI_END:
                (
                    message_format.MeishiEndSchema,
                    self.MeishiEnd,
                    None
                ),
            verbs.MSG_GET_RECOMMENDATION:
                (
                    message_format.GetRecommendationsSchema,
                    self.GetRecommendations,
                    Stats.objects.inc_get_recommendation
                ),
            verbs.MSG_SET_RECO_ACTION:
                (
                    message_format.SetRecoActionSchema,
                    self.SetRecoAction,
                    Stats.objects.inc_set_reco,
                ),
            verbs.MSG_GET_COMMON_CONNECTIONS:
                (
                    message_format.GetCommonConnectionsSchema,
                    self.GetCommonConnections,
                    Stats.objects.inc_get_common_connections,
                ),
            verbs.MSG_GET_VIDEO_THUMBNAIL:
                (
                    message_format.GetVideoThumbnailSchema,
                    self.GetVideoThumbnailUrl,
                    Stats.objects.inc_video_thumbnail
                ),
            verbs.MSG_ENTITY_CREATE:
                (
                    message_format.EntityCreateSchema,
                    self.EntityCreate,
                    Stats.objects.inc_entity_create,
                ),

            verbs.MSG_ENTITY_DESTROY:
                (
                    message_format.EntityDestroySchema,
                    self.EntityDestroy,
                    Stats.objects.inc_entity_destroy,
                ),
            verbs.MSG_ENTITY_EDIT:
                (
                    message_format.EntityEditSchema,
                    self.EntityEdit,
                    Stats.objects.inc_entity_edit,
                ),
            verbs.MSG_ENTITY_JOIN:
                (
                    message_format.EntityJoinSchema,
                    self.EntityJoin,
                    Stats.objects.inc_entity_join
                ),
            verbs.MSG_ENTITY_LEAVE:
                (
                    message_format.EntityLeaveSchema,
                    self.EntityLeave,
                    Stats.objects.inc_entity_leave
                ),
            verbs.MSG_ENTITY_QUERY:
                (
                    message_format.EntityQuerySchema,
                    self.EntityQuery,
                    Stats.objects.inc_entity_query
                ),
            verbs.MSG_MY_ENTITIES:
                (
                    message_format.MyEntitiesSchema,
                    self.MyEntities,
                    Stats.objects.inc_my_entities
                ),
            verbs.MSG_ENTITY_SUMMARY:
                (
                    message_format.EntityDetailsSchema,
                    self.EntityDetails,
                    Stats.objects.inc_entity_summary
                ),
            verbs.MSG_ENTITY_DETAILS:
                (
                    message_format.EntityDetailsSchema,
                    self.EntityDetails,
                    Stats.objects.inc_entity_details
                ),
            verbs.MSG_GET_EVENTS:
                (
                    message_format.EventsGetSchema,
                    self.EventsGet,
                    Stats.objects.inc_events_get
                ),
            verbs.MSG_ENTITIES_ENGAGE:
                (
                    message_format.EntitiesEngageSchema,
                    self.EntitiesEngage,
                    Stats.objects.inc_entities_engage
                )
        }

        # update location since it may have changed
        if self.msg_has_location() and not self.msg_is_initial():
            self.app_userprofile.create_or_update_location(
                self.lat,
                self.lng)

        # process
        response = msgTypesValidatorsAndHandlers[self.msg_id][HANDLER]()

        # bump stats
        if msgTypesValidatorsAndHandlers[self.msg_id][STATS]:
            msgTypesValidatorsAndHandlers[self.msg_id][STATS](self.user_stats, self.global_stats)

        self.header_post_process()
        return response

    def header_post_process(self):
        #make the user as alive
        if not self.msg_is_initial():
            self.app_userprofile.online()

    def PhoneCheckRequest(self):
        device_id = self.header['device_id']
        username = self.sender['username']
        response_mode = self.sender['response_mode']
        response_target = self.sender['target']

        #AA_TODO: security check for checkMode type
        k_user = (settings.PHONE_CHECK_USER_KEY % username)
        k_device_id = (settings.PHONE_CHECK_DEVICE_ID_KEY % username)
        k_rand = (settings.PHONE_CHECK_USER_RAND_KEY % username)
        k_retry = (settings.PHONE_CHECK_USER_RETRY_KEY % username)

        rand_val = random.randint(settings.PHONE_CHECK_RAND_LOW, settings.PHONE_CHECK_RAND_HI)
        d = cache.get_many([k_user, k_device_id, k_rand, k_retry])

        if d.has_key(k_user):
            # sms/nexmo issues. Lets store upto 3 passcodes
            if len(d[k_rand]) >= 3:
                self.response.error_response(err.PHONE_CHECK_RETRY_EXCEEDED)
                return self.response

            d[k_rand].append(rand_val)
            cache.set_many(d)
        else:
            d = dict()
            #new req, generate random num
            d[k_user] = username
            d[k_device_id] = device_id
            d[k_rand] = [rand_val]
            d[k_retry] = 1
            cache.set_many(d, timeout=settings.PHONE_CHECK_TIMEOUT)

        #send a text with the rand
        if settings.PHONE_CHECK:
            msg = wizlib.choose_nexmo_config(response_target)
            if not msg:
                self.response.error_response(err.INVALID_MESSAGE)
                return self.response

            msg['to'] = response_target
            if response_mode == "voice":
                keystr = str(d[k_rand])
                keystr = str.format(','.join([keystr[i:i+1] for i in range(0, len(keystr))]))
                msg['servicetype'] = "tts"
                msg['text'] = \
                    settings.PHONE_CHECK_RESPONSE_VOICE_GREETING % \
                    keystr
            elif response_mode == "sms":
                msg['servicetype'] = "sms"
                msg['text'] = settings.PHONE_CHECK_RESPONSE_SMS_GREETING % \
                               rand_val
            else:
                self.response.error_response(err.INVALID_MESSAGE)
                return self.response

            sms = NexmoMessage(msg)
            sms.set_text_info(msg['text'])
            response = sms.send_request()
            if not response:
                #some error...let the app know
                self.response.error_response(err.NEXMO_SMS_SEND_FAILED)
                logger.error('nexmo send via (%s) failed to (%s)', response_mode, response_target)
                return self.response

        if self.sender.has_key('test_mode'):
            #AA TODO: got to make this tighter/secure
            self.response.add_data("challenge_key", d[k_rand])

        return self.response

    def PhoneCheckResponse(self):
        username = self.sender['username']
        device_id = self.header['device_id']
        challenge_response = self.sender['response_key']

        if not (username and challenge_response):
            self.response.error_response(err.PHONE_CHECK_CHALLENGE_RESPONSE_DENIED)
            return self.response

        k_user = (settings.PHONE_CHECK_USER_KEY % username)
        k_rand = (settings.PHONE_CHECK_USER_RAND_KEY % username)
        k_retry = (settings.PHONE_CHECK_USER_RETRY_KEY % username)
        k_device_id = (settings.PHONE_CHECK_DEVICE_ID_KEY % username)

        d = cache.get_many([k_user, k_device_id, k_rand, k_retry])
        logger.info( "cached value for phone_check_xx {%s}", d)

        if not (d.has_key(k_user) and
                        d.has_key(k_rand) and
                        d.has_key(k_retry) and
                        d.has_key(k_device_id)):
            cache.delete_many([k_user, k_rand, k_retry, k_device_id])
            self.response.error_response(err.PHONE_CHECK_TIMEOUT_EXCEEDED)
            return self.response

        if d[k_retry] > settings.MAX_PHONE_CHECK_RETRIES:
            cache.delete_many([k_user, k_rand, k_retry, k_device_id])
            self.response.error_response(err.PHONE_CHECK_RETRY_EXCEEDED)
            logger.info('{%s} exceeded retry count', k_user)
            return self.response
        else:
            cache.incr(k_retry)

        if device_id != d[k_device_id]:
            logger.info('{%s} invalid device_id', k_user)
            cache.delete_many([k_user, k_rand, k_retry, k_device_id])
            self.response.error_response(err.PHONE_CHECK_CHALLENGE_RESPONSE_INVALID_DEVICE)
            return self.response

        if settings.PHONE_CHECK and int(challenge_response) not in d[k_rand]:
            logger.info('{%s, [%s]!=[%s]} invalid challenge response', k_user, challenge_response, d[k_rand])
            self.response.error_response(err.PHONE_CHECK_CHALLENGE_RESPONSE_DENIED)
            return self.response

        # response is valid. create user here and send back user_id
        user, created = User.objects.get_or_create(username=username)

        if created:
            #AA TODO: Generate hash from device_id and user_id
            #and maybe phone number
            password = UserProfile.objects.gen_password(device_id, str(user.profile.userid))
            user.set_password(password)
            user.save()
            app_user = user.profile.create_user_type(UserProfile.APP_USER)
            app_user.device_id = device_id
        else:
            app_user = user.profile.app_user()
            if device_id != app_user.device_id:
                app_user.device_id = device_id

                #device_id is part of password, reset password to reflect new device_id
                password = UserProfile.objects.gen_password(device_id, str(user.profile.userid))
                user.set_password(password)
                user.save()

            # mark for sync if profile is activated
            if user.profile.activated:
                app_user.do_sync = True

        app_user.save()

        # all done. clear cache
        cache.delete_many([k_user, k_device_id, k_rand, k_retry])

        user.profile.save()

        self.response.add_data("user_id", str(user.profile.userid))
        return self.response

    def Login(self):
        try:
            self.username = self.sender['username']
            self.user = User.objects.get(username=self.username)
            self.password = self.sender['password']
            auth = authenticate(username=self.username, password=self.password)
            if auth is None:
                #invalid password
                self.response.error_response(err.AUTHENTICATION_FAILED)
                return self.response

            self.response.add_data("wizuser_id", self.user.pk)
        except:
            self.security_exception()
            self.response.ignore()

        return self.response

    def Register(self):
        #fill in device details
        try:
            self.app_userprofile.device_type = self.sender['device_type']
        except:
            pass

        self.app_userprofile.reg_token = self.sender['reg_token']

        if self.app_userprofile.do_sync:
            #sync all syncables
            s = self.app_userprofile.do_resync()
            if 'wizcard' in s:
                self.response.add_data("wizcard", s['wizcard'])
                self.response.add_data("wizcard", s['wizcard'])
                if 'wizconnections' in s:
                    self.response.add_data("rolodex", s['wizconnections'])
                if 'context' in s:
                    self.response.add_data("context", s['context'])
                if 'wizcard_flicks' in s:
                    self.response.add_data("wizcard_flicks", s['wizcard_flicks'])
                if 'tables' in s:
                    self.response.add_data("tables", s['tables'])
                if 'flick_picks' in s:
                    self.response.add_data("flick_picks", s["flick_picks"])
                if 'deadcards' in s:
                    self.response.add_data("deadcards", s["deadcards"])

                self.userprofile.activated = True
            self.app_userprofile.do_sync = False
        self.app_userprofile.save()

        return self.response

    def LocationUpdate(self):
        #update location in ptree
        self.app_userprofile.create_or_update_location(self.lat, self.lng)
        return self.response

    def ContactsUpload(self):
        # 'prefix': "", 'country_code": "", ab_entry: [{name:"", phone:phone, emails:email}, {}]
        int_prefix = self.receiver.get('prefix', None)
        country_code = self.receiver.get('country_code', None)
        ab_list = self.receiver.get('ab_list')

        contacts_upload_task.delay(self.user, int_prefix, country_code, ab_list)

        # AA:TODO ideally this would be better is signal is sent after above task finishes
        # for that we'll need to chain tasks and wrap this signal sending in a task as well
        genreco.send(self.user, recotarget=self.user.id)
        return self.response

    def ContactsVerify(self):
        verify_phone_list = self.receiver.get('verify_phones', [])
        verify_email_list = self.receiver.get('verify_emails', [])
        lp = []
        le = []

        phone_count = 0
        for phone_number in verify_phone_list:
            wizcard = UserProfile.objects.check_user_exists('phone',
                                                            phone_number)

            if wizcard:
                if self.user == wizcard.user:
                    continue

                d = dict()
                d['phoneNum'] = phone_number
                d['wizuser_id'] = wizcard.user_id
                if Wizcard.objects.are_wizconnections(
                        self.user.wizcard,
                        wizcard):
                    d['tag'] = "connected"
                else:
                    d['tag'] = "other"

                wc = WizcardSerializerL1(wizcard, many=True, **self.user_context)

                d['wizcard'] = wc

                phone_count += 1
                lp.append(d)

        if phone_count:
            self.response.add_data("phone_count", phone_count)
            self.response.add_data("verified_phones", lp)

        email_count = 0
        for email in verify_email_list:
            wizcard = UserProfile.objects.check_user_exists('email',
                                                            email)
            if wizcard:
                d = dict()
                d['email'] = email
                d['wizuser_id'] = wizcard.user_id
                if Wizcard.objects.are_wizconnections(
                        self.user.wizcard,
                        wizcard):
                    d['tag'] = "connected"
                elif self.user == wizcard.user:
                    d['tag'] = "own"
                else:
                    d['tag'] = "other"

                wc = WizcardSerializerL1(wizcard, many=True, **self.user_context)
                d['wizcard'] = wc

                email_count += 1
                le.append(d)
        if email_count:
            self.response.add_data("email_count", email_count)
            self.response.add_data("verified_emails", le)
        self.response.add_data("count", phone_count + email_count)

        return self.response

    def NotificationsGet(self):
        notifications = Notification.objects.unread(self.user)
        notifResponse = NotifResponse(notifications)

        #i will be activated when I have a wizcard
        if not self.userprofile.activated:
            return self.response

        if self.sender.has_key('reco_actions'):
            recoactions = self.sender['reco_actions']
            for rectuple in recoactions:
                recid = rectuple['reco_id']
                recaction = rectuple['action']
                try:
                    reco_object = UserRecommendation.objects.get(id=recid)
                    reco_object.setAction(recaction)
                except:
                    logger.warning('Recommendation Action failed for %s', str(recid))
                    pass

            #AnandR: Ideally we should generate recommendations for every action to check their like and dislike but we are not using the feedback now so commenting this out
            #if recoactions:
                #genreco.send(self.user, recotarget=str(self.user.id))

        if self.lat is None and self.lng is None:
            try:
                self.lat = self.userprofile.location.get().lat
                self.lng = self.userprofile.location.get().lng
            except:
                #maybe location timedout. Shouldn't happen if messages from app
                #are coming correctly...
                logger.warning('No location information available')
                return self.response

        #any wizcards dropped nearby
        #AA:TODO: Use come caching framework to cache these
        # flicked_wizcards, count = WizcardFlick.objects.lookup(
        #     self.lat,
        #     self.lng,
        #     settings.DEFAULT_MAX_LOOKUP_RESULTS)
        # if count:
        #     notifResponse.notifFlickedWizcardsLookup(count,
        #                                              self.user, flicked_wizcards)

        users, count = self.app_userprofile.lookup(
            settings.DEFAULT_MAX_LOOKUP_RESULTS)
        if count:
            notifResponse.notifUserLookup(
                count,
                self.user,
                users)

        reco_count = self.app_userprofile.reco_ready
        if reco_count:
            self.app_userprofile.reco_ready = 0

        tables, count = VirtualTable.objects.lookup(
            self.lat,
            self.lng,
            settings.DEFAULT_MAX_LOOKUP_RESULTS)
        if count:
            notifResponse.notifTableLookup(count, self.user, tables)

        Notification.objects.mark_specific_as_read(notifications)

        #tickle the timer to keep it going and update the location if required
        self.app_userprofile.create_or_update_location(self.lat, self.lng)

        self.response = notifResponse
        return self.response

    def RolodexEdit(self):
        wizcard1 = self.user.wizcard
        try:
            wizcard2 = Wizcard.objects.get(id=self.receiver['wizcard_id'])
        except ObjectDoesNotExist:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        if 'notes' in self.receiver:
            # get conn represented by w1<-w2
            rel = wizcard2.get_relationship(wizcard1)
            rel.cctx.notes = self.receiver['notes']['note']
            rel.cctx.notes_last_saved = self.receiver['notes']['last_saved']
            rel.save()

        return self.response

    def WizcardEdit(self):
        modify = False
        user_modify = False

        wizcard, created = Wizcard.objects.get_or_create(user=self.user)
        cc = ContactContainer.objects.create(wizcard=wizcard) if created else wizcard.contact_container.all()[0]

        # set activated to true on creation and if not already set. There can be a scenario when one mode of onboarding
        # (say ocr) failed and the user re-onboarded from a different mode. In this case there will be a wizcard
        # present, from the failed iteration but not activated.
        if created or not self.userprofile.activated:
            self.userprofile.activated = True
            self.userprofile.save()

        #AA:TODO: Change app to call this phone as well
        if 'phone' in self.sender or 'phone1' in self.sender:
            phone = self.sender['phone'] if self.sender.has_key('phone') else self.sender['phone1']

            if wizcard.phone != phone:
                wizcard.phone = phone
                modify = True

        if 'first_name' in self.sender:
            first_name = self.sender['first_name']
            if self.user.first_name != first_name:
                self.user.first_name = self.sender['first_name']
                modify = True
                user_modify = True

        if 'last_name' in self.sender:
            last_name = self.sender['last_name']
            if self.user.last_name != last_name:
                self.user.last_name = self.sender['last_name']
                modify = True
                user_modify = True

        if 'email' in self.sender:
            email = self.sender['email']
            if wizcard.email != email:
                wizcard.email = email
                modify = True

        if 'ext_fields' in self.sender and self.sender['ext_fields']:
            wizcard.ext_fields = self.sender['ext_fields'].copy()
            modify = True

        if 'media' in self.sender:
            # delete any existing media
            wizcard.media.all().delete()

            # not liking this way. Need to remove media_id since app is not able to remove it
            for m in self.sender['media']:
                discard = m.pop('media_id', None)

            mw = media_create.send(sender=self.user, objs=self.sender['media'])
            for m in mw[0][1]:
                m.related_connect(wizcard.media)

        if 'contact_container' in self.sender:
            contact_container_list = self.sender['contact_container']
            modify = True

            for count, contactItem in enumerate(contact_container_list):
                if 'title' in contactItem:
                    cc.title = contactItem['title']
                if 'company' in contactItem:
                    cc.company = contactItem['company']
                if 'phone' in contactItem:
                    cc.phone = contactItem['phone']

                cc.media.all().delete()
                if 'media' in contactItem:
                    for m in contactItem['media']:
                        discard = m.pop('media_id', None)

                    mc = media_create.send(sender=self.user, objs=contactItem['media'])
                    for m in mc[0][1]:
                        m.related_connect(cc.media)

                cc.save()

        if user_modify:
            self.user.save()

        if created or modify:
            vcard = create_vcard(wizcard)
            wizcard.vcard = vcard

        wizcard.save()

        # Check for admin user connection and create it
        admin_user = UserProfile.objects.get_admin_user()
        admin_conn = wizcard.get_relationship(admin_user.wizcard)

        if not admin_conn:
            # connect implicitly with admin wizcard

            try:
                location_str = wizlib.reverse_geo_from_latlng(
                    self.app_userprofile.location.get().lat,
                    self.app_userprofile.location.get().lng
                )
            except:
                logging.error("couldn't get location for user [%s]", self.userprofile.userid)
                location_str = ""

            # me->admin(P)
            cctx1 = ConnectionContext(
                asset_obj=wizcard,
                connection_mode=verbs.INVITE_VERBS[verbs.WIZCARD_CONNECT_T],
                location=location_str)
            Wizcard.objects.cardit(wizcard, admin_user.wizcard, status=verbs.PENDING, cctx=cctx1)

            # me(A)<-admin
            cctx2 = ConnectionContext(
                asset_obj=admin_user.wizcard,
                connection_mode=verbs.INVITE_VERBS[verbs.WIZCARD_CONNECT_T],
                location=location_str)
            Wizcard.objects.cardit(admin_user.wizcard, wizcard, status=verbs.ACCEPTED, cctx=cctx2)

            # notify me
            rel21 = admin_user.wizcard.get_relationship(wizcard)

            notify.send(
                admin_user.wizcard.user, recipient=wizcard.user,
                verb=verbs.WIZREQ_T[0],
                target=admin_user.wizcard,
                action_object=rel21)

        # check if futureUser states exist for this phone or email
        future_users = FutureUser.objects.check_future_user(wizcard.email, wizcard.phone)

        for f in future_users:
            f.generate_self_invite(self.user)

        if future_users.count():
            future_users.delete()

        # flood to contacts
        if modify:
            wizcard.flood()

        if created:
            email_trigger.send(self.user, trigger=EmailEvent.NEWUSER, source=self.user.wizcard, target=wizcard)

        self.response.add_data("wizcard", WizcardSerializerL2(wizcard).data)
        return self.response

    # Set both sides to accept. There should already be wizcard1(me)->wizcard2(him) in ACCEPT
    # and wizcard2->wizcard1 in PENDING.
    # NOTE: A->B doesn't denote direction of request. It denotes that B is FOLLOWING A. ie
    # B has A's wizcard in roldex
    def WizcardAccept(self):
        status = []
        verb1 = verbs.WIZREQ_T[0]
        verb2 = verbs.WIZREQ_T[0]

        try:
            wizcard1 = self.user.wizcard
            flag = self.sender.get('flag', "accept")
            #AA TODO: Change to wizcardID

            try:
                wizcard2 = Wizcard.objects.get(id=self.receiver['wizcard_id'])
                self.r_user = User.objects.get(id=self.receiver['wizuser_id'])
            except:
                self.r_user = User.objects.get(id=self.receiver['wizuser_id'])
                wizcard2 = self.r_user.wizcard

        except KeyError:
            self.security_exception()
            self.response.ignore()
            return self.response
        except ObjectDoesNotExist:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        if 'notif_id' in self.sender and self.sender['notif_id']:
                # now we know that the App has acted upon this notification
                # we will use this flag during resync notifs and send unacted-upon
                # notifs to user
                Notification.objects.get(id=self.sender['notif_id']).set_acted(True)

        rel12 = wizcard1.get_relationship(wizcard2)
        rel21 = wizcard2.get_relationship(wizcard1)

        # safeguard against app bug. Accept only when we're in the right state, ignore otherwise
        if rel21.status == verbs.ACCEPTED:
            # already connected...duplicate req...Ignore
            status.append(
                dict(
                    status=Wizcard.objects.get_connection_status(wizcard1, wizcard2),
                    wizcard_id=wizcard2.id)
            )
            self.response.add_data("status", status)
            return self.response

        if flag == "reaccept" or flag == "unarchive":
            # add-to-rolodex case. Happens when user had previously declined/deleted this guy
            try:
                location_str = wizlib.reverse_geo_from_latlng(
                    self.app_userprofile.location.get().lat,
                    self.app_userprofile.location.get().lng
                )
            except:
                logging.error("couldn't get location for user [%s]", self.userprofile.userid)
                location_str = ""

            cctx = ConnectionContext(
                asset_obj=wizcard2,
                connection_mode=verbs.INVITE_VERBS[verbs.WIZCARD_CONNECT_U],
                location=location_str
            )
            Wizcard.objects.becard(wizcard2, wizcard1, cctx)
        elif rel12.status == verbs.DELETED:
            # err 25 case
            # remove arrows and set to clean state
            Wizcard.objects.uncardit(wizcard2, wizcard1, soft=False)
            Wizcard.objects.uncardit(wizcard1, wizcard2, soft=False)
            self.response.error_response(err.REVERSE_INVITE)
            return self.response
        else:
            Wizcard.objects.becard(wizcard2, wizcard1)

        if wizcard1.get_relationship(wizcard2).status != verbs.ACCEPTED:
            verb1 = verbs.WIZREQ_T_HALF[0]
            verb2 = None
        # Q notif to both sides.
        notify.send(self.r_user,
                    recipient=self.user,
                    verb=verb1,
                    target=wizcard2,
                    action_object=rel21)

        # Q notif for wizcard2 to change his half card to full
        if verb2:
            notify.send(self.user,
                        recipient=self.r_user,
                        verb=verb2,
                        target=wizcard1,
                        action_object=rel12)

        status.append(
            dict(status=Wizcard.objects.get_connection_status(wizcard1, wizcard2),
                 wizcard_id=wizcard2.id)
        )
        self.response.add_data("status", status)
        genreco.send(self.user, recotarget=self.user.id)
        return self.response

    def WizConnectionRequestDecline(self):
        try:
            wizcard1 = self.user.wizcard
            wizcard2 = Wizcard.objects.get(id=self.receiver['wizcard_id'])
        except KeyError:
            self.security_exception()
            self.response.ignore()
            return self.response
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        if wizcard1.get_relationship(wizcard2).status is verbs.DELETED:
            # error 25 scenario for declined case. We need to remove both arrows
            Wizcard.objects.uncardit(wizcard2, wizcard1, soft=False)
            Wizcard.objects.uncardit(wizcard1, wizcard2, soft=False)
        else:
            Wizcard.objects.uncard(wizcard2, wizcard1)

        n_id = self.sender['notif_id']
        n = Notification.objects.get(id=n_id)

        # now we know that the App has acted upon this notification
        #  we will use this flag during resync notifs and send unacted-upon
        #  notifs to user
        n.set_acted(True)

        return self.response

    def WizcardRolodexDelete(self):
        try:
            wizcard1 = self.user.wizcard
            wizcards = self.receiver['wizcard_ids']

            for w in wizcards:
                try:
                    w_id = w.get("wizcard_id")
                    dead_card = w.get("dead_card")
                except:
                    self.response.error_response(err.INVALID_MESSAGE)
                    return self.response

                if dead_card:
                    try:
                        wizcard2 = DeadCard.objects.get(id=w_id)
                    except:
                        self.response.error_response(err.OBJECT_DOESNT_EXIST)
                        return self.response

                    wizcard2.delete()
                else:
                    wizcard2 = Wizcard.objects.get(id=w_id)
                    # If this is a delete right after an invite was sent by wizcard1 then we have to remove
                    # notif 2 for wizcard2 and set rel to clean state
                    if wizcard1.get_relationship(wizcard2).status == verbs.PENDING:
                        n = Notification.objects.filter(
                                recipient=wizcard2.user,
                                target_object_id=wizcard1.id,
                                readed=False,
                                verb=verbs.WIZREQ_U[0])
                        if n.count():
                            map(lambda x: x.delete(), n)
                            Wizcard.objects.uncardit(wizcard2, wizcard1, soft=False)
                            Wizcard.objects.uncardit(wizcard1, wizcard2, soft=False)
                        else:
                            # w2 has read it, but not acted. delete state w2->w1
                            # no notif in this case. Err25 will be triggered when w2 acts on it
                            Wizcard.objects.uncardit(wizcard2, wizcard1)
                    else:
                        # regular case.
                        Wizcard.objects.uncardit(wizcard2, wizcard1)
                        # Q a notif to other guy so that the app on the other side can react
                        notify.send(self.user, recipient=wizcard2.user,
                                    verb=verbs.WIZCARD_REVOKE[0],
                                    target=wizcard1)
        except KeyError:
            self.security_exception()
            self.response.ignore()

        return self.response

    def WizcardRolodexArchivedCards(self):
        out = ""
        try:
            wizcard = self.user.wizcard
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        w = wizcard.get_deleted()
        self.response.add_data("wizcards", WizcardSerializerL2(w, many=True, **self.user_context).data)

        return self.response

    def WizcardFlick(self):
        try:
            wizcard = self.user.wizcard
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        #app sends in minutes
        timeout = self.sender['timeout']
        a_created = self.sender['created']

        if self.lat is None and self.lng is None:
            try:
                self.lat = self.app_userprofile.location.get().lat
                self.lng = self.app_userprofile.location.get().lng
            except:
                #should not happen since app is expected to send a register or something
                #everytime it wakes up...however, network issues can cause app to go offline
                #while still in foreground. No option but to send back error response to app
                #However, if app had included location information, then we will
                #update_location before getting here and be ok
                self.response.error_response(err.LOCATION_UNKNOWN)
                return self.response

        flick_card = wizcard.check_flick_duplicates(self.lat, self.lng)

        if flick_card:
            #we are going to add the new timeout to timeRemaining from
            #previous flick

            t = flick_card.location.get().extend_timer(timeout)
            self.response.add_data("duplicate", True)
            self.response.add_data("timeout", t.timeout_value/60)
        else:
            try:
                location = wizlib.reverse_geo_from_latlng(self.lat, self.lng)
            except:
                location = ""

            self.response.add_data("city", wizlib.format_location_name(location))

            flick_card = WizcardFlick.objects.create(wizcard=wizcard,
                                                     lat=self.lat,
                                                     lng=self.lng,
                                                     timeout=timeout,
                                                     reverse_geo_name=location,
                                                     a_created = a_created)
            location = flick_card.create_location(self.lat, self.lng)
            location.start_timer(timeout)

        #AA:TODO put all this in fields.py with template
        self.response.add_data("flickCardID", flick_card.pk)
        return self.response

    def WizcardFlickPick(self):
        #wizcard1 is following wizcard2
        try:
            wizcard1 = self.user.wizcard
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response
        try:
            for flick_id in self.receiver['flickCardIDs']:
                flick_card = WizcardFlick.objects.get(id=flick_id)
                wizcard2 = flick_card.wizcard

                cctx = ConnectionContext(asset_obj=flick_card)
                #associate flick with user
                flick_card.flick_pickers.add(wizcard1)
                #create wizcard2->wizcard1 relationship and accept
                rel = Wizcard.objects.cardit(wizcard2, wizcard1, status=verbs.ACCEPTED, cctx=cctx)
                #Q pick_notif to flicker
                notify.send(self.user, recipient=wizcard2.user,
                            verb=verbs.WIZCARD_FLICK_PICK[0],
                            target=flick_card,
                            action_object=rel)

            return self.response
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

    def WizcardFlickConnect(self):
        #wizcard1 sends implicit connect to wizcard2
        try:
            wizcard1 = self.user.wizcard
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response
        try:
            for flick_id in self.receiver['flickCardIDs']:
                flick_card = WizcardFlick.objects.get(id=flick_id)
                wizcard2 = flick_card.wizcard
                #AA:TODO should existing connectivity be checked ?
                cctx = ConnectionContext(asset_obj=flick_card)
                rel1 = Wizcard.objects.cardit(wizcard1, wizcard2, status=verbs.ACCEPTED, cctx=cctx)
                #rel2 = Wizcard.objects.cardit(wizcard2, wizcard1, status=verbs.ACCEPTED, cctx=cctx)

                #Q implicit exchange to flicker
                notify.send(self.user, recipient=wizcard2.user,
                            verb=verbs.WIZREQ_T[0],
                            target=wizcard1,
                            action_object=rel1)
            return self.response
        except KeyError:
            self.security_exception()
            self.response.ignore()
            return self.response
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

    def WizcardMyFlicks(self):
        self.wizcard = Wizcard.objects.get(id=self.sender['wizcard_id'])
        my_flicked_cards = self.wizcard.flicked_cards.exclude(expired=True)

        count = my_flicked_cards.count()

        # AA: TODO
        if count:
            flicks_s = WizcardSerializerL2(my_flicked_cards, many=True, **self.user_context)
            self.response.add_data("queryResult", flicks_s)
        self.response.add_data("count", count)

        return self.response

    def WizcardFlickWithdraw(self):
        try:
            self.flicked_card = WizcardFlick.objects.get(id=self.sender['flickCardID'])
        except KeyError:
            self.security_exception()
            self.response.ignore()
            return self.response
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        self.flicked_card.delete()
        return self.response

    def WizcardFlickEdit(self):
        try:
            flick_id = self.sender['flickCardID']
            timeout = self.sender['timeout'] * 60
            a_created = self.sender['created']
        except KeyError:
            self.security_exception()
            self.response.ignore()
            return self.response
        try:
            flicked_card = WizcardFlick.objects.get(id=flick_id)
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        flicked_card.a_created = a_created
        flicked_card.timeout = timeout
        flicked_card.save()
        flicked_card.location.get().reset_timer(timeout)

        return self.response

    def WizcardFlickQuery(self):
        if not self.receiver.has_key('name'):
            self.security_exception()
            self.response.ignore()
            return self.response

        result, count = WizcardFlick.objects.query_flicks(self.receiver['name'], None, None)

        if count:
            flicks_s = WizcardFlick.objects.serialize_split(
                self.user.wizcard,
                result)
            self.response.add_data("queryResult", flicks_s)
        self.response.add_data("count", count)

        return self.response

    def WizcardFlickPickers(self):
        try:
            flick_id = self.sender['flickCardID']
        except KeyError:
            self.security_exception()
            self.response.ignore()
            return self.response

        try:
            flicked_card = WizcardFlick.objects.get(id=flick_id)
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        if flicked_card.wizcard.user != self.user:
            self.security_exception()
            self.response.ignore()
            return self.response

        flick_pickers = flicked_card.flick_pickers.all()
        count = flick_pickers.count()

        if count:
            out = Wizcard.objects.serialize(flick_pickers,
                                            template = fields.wizcard_template_brief)
            self.response.add_data("flickPickers", out)

        self.response.add_data("count", count)
        return self.response

    #new message. Combines all kinds of asset types (cards, tables) and
    #receiver types. Includes future handling as part of this
    def WizcardSendAssetToXYZ(self):
        try:
            asset_type = self.sender['asset_type']
            sender_id = self.sender['asset_id']
            receiver_type = self.receiver['receiver_type']
            receivers = self.receiver['receiver_ids']
        except:
            self.security_exception()
            self.response.ignore()
            return self.response

        if asset_type == "wizcard":
            try:
                wizcard = Wizcard.objects.get(id=sender_id)
            except ObjectDoesNotExist:
                self.response.error_response(err.OBJECT_DOESNT_EXIST)
                return self.response

            if self.user.wizcard.id != wizcard.id:
                self.security_exception()
                self.response.ignore()
                return self.response

            self.response = self.WizcardSendWizcardToXYZ(
                wizcard,
                receiver_type,
                receivers)
        elif asset_type == "table":
            try:
                table = VirtualTable.objects.get(id=sender_id)
            except ObjectDoesNotExist:
                self.response.error_response(err.OBJECT_DOESNT_EXIST)
                return self.response
            #creator can fwd private table, anyone (member) can fwd public
            #table
            if not((table.secure and table.get_creator() == self.user) or
                       ((not table.secure) and table.is_joined(self.user))):
                self.response.error_response(err.NOT_AUTHORIZED)
                return self.response

            self.response = self.WizcardSendTableToXYZ(
                table,
                receiver_type,
                receivers)
        else:
            self.security_exception()
            self.response.ignore()
            return self.response

        return self.response

    def WizcardSendWizcardToXYZ(self, wizcard, receiver_type, receivers):
        count = 0
        status = []
        to_notify = True
        from_notify = True

        if receiver_type == verbs.INVITE_VERBS[verbs.WIZCARD_CONNECT_U]:
            # add location to cctx. For nearby based exchange, use
            # senders location (which should be same as receivers too)
            try:
                location_str = wizlib.reverse_geo_from_latlng(
                    self.app_userprofile.location.get().lat,
                    self.app_userprofile.location.get().lng
                )
            except:
                logging.error("couldn't get location for user [%s]", self.userprofile.userid)
                location_str = ""

            numreceivers = len(receivers)

            for _id in receivers:
                r_user = User.objects.get(id=_id)
                r_wizcard = r_user.wizcard

                # IF there are more receivers its ok to fail one silently
                if numreceivers == 1 and self.user.wizcard.id == r_wizcard.id:
                    self.response.error_response(err.SELF_INVITE)
                    return self.response

                rel12 = wizcard.get_relationship(r_wizcard)
                cctx1 = ConnectionContext(
                        asset_obj=wizcard,
                        connection_mode=receiver_type,
                        location=location_str)
                rel21 = r_wizcard.get_relationship(wizcard)
                conn_status = verbs.WIZREQ_U[0]

                if rel12:
                    # wizcard->r_wizcard exists previously ?
                    if rel12.status == verbs.ACCEPTED or rel12.status == verbs.PENDING:
                        if rel21 and rel21.status == verbs.PENDING:
                            conn_status = verbs.WIZREQ_T[0]
                        else:
                            to_notify = False
                    else:
                        # set it to pending. We'll send a notif
                        rel12.reset()
                        rel12.set_context(cctx1)
                else:
                    # create wizcard1->wizcard2
                    rel12 = Wizcard.objects.cardit(wizcard,
                                                   r_wizcard,
                                                   status=verbs.PENDING,
                                                   cctx=cctx1)
                # Q notif for to_wizcard
                if to_notify:
                    notify.send(
                        self.user, recipient=r_user,
                        verb=verbs.WIZREQ_T[0] if receiver_type == verbs.INVITE_VERBS[verbs.WIZCARD_CONNECT_T] else
                        conn_status,
                        target=wizcard,
                        action_object=rel12)

                # Context should always have the from_wizcard and for the time being sender's location - Still debating
                cctx2 = ConnectionContext(
                    asset_obj=r_wizcard,
                    connection_mode=receiver_type,
                    location=location_str
                )

                # reverse connection, if exists, should be deleted/declined
                if rel21:
                    if rel21.status == verbs.ACCEPTED:
                        from_notify = False
                    else:
                        # Handles one side deleted or both deleted and again trying to connect
                        if rel21.status == verbs.DELETED:
                            if rel12.status == verbs.ACCEPTED:
                                conn_status = verbs.WIZREQ_T[0]
                            else:
                                conn_status = verbs.WIZREQ_T_HALF[0]
                        else:
                            # Handles 2 invites going out simultaneously like both pressing invite to connect
                            conn_status = verbs.WIZREQ_T[0]
                        # set it to accepted. We'll send a notif
                        rel21.set_context(cctx2)
                        rel21.accept()
                else:
                    # create and accept implicitly wizcard2->wizcard1
                    rel21 = Wizcard.objects.cardit(r_wizcard,
                                                   wizcard,
                                                   verbs.ACCEPTED,
                                                   cctx=cctx2
                                                   )
                    conn_status = verbs.WIZREQ_T_HALF[0]

                # Q notif for from_wizcard. While app has (most of) this info, it's missing location. So
                # let server push this via notif 1.
                if from_notify:
                    notify.send(r_user, recipient=self.user,
                                verb=conn_status,
                                target=r_wizcard,
                                action_object=rel21)

                count += 1
                status.append(dict(
                    status=Wizcard.objects.get_connection_status(wizcard, r_wizcard),
                    wizcard_id=r_wizcard.id)
                )
            self.response.add_data("count", count)
            self.response.add_data("status", status)
        elif receiver_type in [verbs.INVITE_VERBS[verbs.SMS_INVITE], verbs.INVITE_VERBS[verbs.EMAIL_INVITE]]:
            # future user handling
            self.do_future_user(wizcard, receiver_type, receivers)

        return self.response

    def WizcardSendTableToXYZ(self, table, receiver_type, receivers):
        #AA TODO: move the 'wiz_xyz' strings into verbs file
        if receiver_type in ['wiz_untrusted', 'wiz_trusted']:
            #receiver_ids has wizuser_ids
            for _id in receivers:
                r_user = User.objects.get(id=_id)
                cctx = ConnectionContext(
                    asset_obj=table,
                    connection_mode=receiver_type,
                )

                #Q this to the receiver
                notify.send(self.user, recipient=r_user,
                            verb=verbs.WIZCARD_TABLE_INVITE[0],
                            target=table)
        elif receiver_type in [verbs.INVITE_VERBS[verbs.SMS_INVITE],
                               verbs.INVITE_VERBS[verbs.EMAIL_INVITE]]:
            # create future user
            self.do_future_user(table, receiver_type, receivers)

        return self.response

    def do_future_user(self, obj, receiver_type, receivers):
        for r in receivers:
            # for a typed out email/sms, the user may still be in wiz
            wizcard = UserProfile.objects.check_user_exists(receiver_type, r)

            if wizcard:
                # self check
                if self.user.wizcard.id == wizcard.id:
                    continue

                if ContentType.objects.get_for_model(obj) == \
                        ContentType.objects.get(model="wizcard"):
                    rel12 = obj.get_relationship(wizcard)
                    if not rel12:
                        cctx1 = ConnectionContext(
                            asset_obj=obj,
                            connection_mode=receiver_type,
                        )
                        rel12 = Wizcard.objects.cardit(obj,
                                                       wizcard,
                                                       status=verbs.PENDING,
                                                       cctx=cctx1)
                        # Q notif for to_wizcard
                        notify.send(self.user, recipient=wizcard.user,
                                    verb=verbs.WIZREQ_U[0],
                                    target=obj,
                                    action_object=rel12)
                    elif rel12.status == verbs.DECLINED or \
                                    rel12.status == verbs.DELETED:
                        # reset 2 to pending. Yes there is a potential "don't bother me" angle
                        # to this..but better to promote connections
                        rel12.reset()
                        notify.send(self.user, recipient=wizcard.user,
                                    verb=verbs.WIZREQ_U[0],
                                    target=obj,
                                    action_object=rel12)

                    rel21 = wizcard.get_relationship(obj)
                    cctx2 = ConnectionContext(asset_obj = wizcard,connection_mode=receiver_type)
                    if not rel21:
                        # create and accept implicitly wizcard2->wizcard1 with cctx->asset_obj as the from_wizcard
                        rel21 = Wizcard.objects.cardit(wizcard,
                                                       obj,
                                                       status=verbs.ACCEPTED,
                                                       cctx=cctx2)
                        notify.send(wizcard.user, recipient=self.user,
                                    verb=verbs.WIZREQ_T_HALF[0],
                                    target=wizcard,
                                    action_object=rel21)

                    elif rel21.status == verbs.DECLINED or \
                                    rel21.status == verbs.DELETED:
                        # This is to handle cases where its deleted but invite sent again through SMS or email
                        if rel12.status == verbs.PENDING:
                            rel21.status = verbs.ACCEPTED
                            rel21.save()
                            conn_status = verbs.WIZREQ_T_HALF[0]
                        else:
                        # if declined/deleted, follower-d case, full card can be added
                            rel21.set_context(cctx2)
                            rel21.accept()
                            conn_status = verbs.WIZREQ_T[0]

                        notify.send(wizcard.user, recipient=self.user,
                                    verb=conn_status,
                                    target=wizcard,
                                    action_object=rel21)
                    else:
                        # was already in ACCEPTED, leave as-is.
                        # if was in PENDING, it means he has previously sent us a req.
                        # so that an unacted req should exist in the App.
                        # Better to leave as is and have user use the req to connect
                        pass

                elif ContentType.objects.get_for_model(obj) == \
                        ContentType.objects.get(model="virtualtable"):
                    #Q this to the receiver
                    notify.send(self.user, recipient=wizcard.user,
                                verb=verbs.WIZCARD_TABLE_INVITE[0],
                                target=obj)

                if receiver_type == verbs.INVITE_VERBS[verbs.EMAIL_INVITE]:
                    email_trigger.send(self.user, trigger=EmailEvent.INVITED, source=self.user.wizcard, target=wizcard)
            else:
                FutureUser.objects.get_or_create(
                        inviter=self.user,
                        content_type=ContentType.objects.get_for_model(obj),
                        object_id=obj.id,
                        phone=r if receiver_type == verbs.INVITE_VERBS[verbs.SMS_INVITE] else "",
                        email=r if receiver_type == verbs.INVITE_VERBS[verbs.EMAIL_INVITE] else ""
                )
                if receiver_type == verbs.INVITE_VERBS[verbs.EMAIL_INVITE]:
                    email_trigger.send(self.user, trigger=EmailEvent.INVITED, source=self.user.wizcard, to_email=r)

    def UserQuery(self):
        try:
            name = self.receiver['name']
        except:
            name = None
        try:
            phone = self.receiver['phone']
        except:
            phone = None
        try:
            email = self.receiver['email']
        except:
            email = None

        result, count = Wizcard.objects.query_users(self.user, name, phone, email)

        if count:
            out = WizcardSerializerL1(result, many=True, **self.user_context).data
            self.response.add_data("queryResult", out)
        self.response.add_data("count", count)

        return self.response

    def GetCommonConnections(self):
        MAX_L1_LIST_VIEW = 3

        try:
            wizcard1 = Wizcard.objects.get(id=self.sender['wizcard_id'])
            wizcard2 = Wizcard.objects.get(id=self.receiver['wizcard_id'])
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        full = self.sender.get('full', False)

        # get common connections between the 2
        s1 = set(wizcard1.get_following_no_admin())
        s2 = set(wizcard2.get_following_no_admin())

        common = list(s1 & s2)
        count = len(common)
        split = None if count < MAX_L1_LIST_VIEW or full else MAX_L1_LIST_VIEW
        if count:
            common_s = WizcardSerializerL1(common[:split], many=True, **self.user_context).data
            self.response.add_data("wizcards", common_s)
        self.response.add_data("total", count)

        return self.response

    def GetVideoThumbnailUrl(self):
        video_url = self.sender['video_url']

        try:
            resp = noembed.embed(video_url)
            video_thumbnail_url = resp.thumbnail_url
        except:
            # Try with ffmpeg
            VIDEO_SEEK_SECONDS = 5
            OUTFILE_PATH = "/tmp/"
            video_url = self.sender['video_url']
            rand_val = random.randint(settings.PHONE_CHECK_RAND_LOW, settings.PHONE_CHECK_RAND_HI)

            filename = "thumbnail_video-%s.%s.jpg" % (rand_val, now().strftime ("%Y-%m-%d %H:%M"))
            outfile = OUTFILE_PATH+filename

            c = Converter()
            try:
                c.thumbnail(video_url, VIDEO_SEEK_SECONDS, outfile, size='160:120')
            except:
                self.response.error_response(err.EMBED_FAILED)
                return self.response

            # upload file to aws and get url
            remote_path = '/thumbnails/' + filename

            try:
                video_thumbnail_url = wizlib.uploadtoS3(outfile, remote_dir=remote_path)
            except:
                self.response.error_response(err.EMBED_FAILED)
                return self.response

        self.response.add_data("video_thumbnail_url", video_thumbnail_url)
        return self.response

    def WizcardGetDetail(self):
        try:
            wizcard = Wizcard.objects.get(id=self.receiver['wizcard_id'])
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        s = WizcardSerializerL1 if self.app_settings.is_profile_private else WizcardSerializerL2
        out = WizcardSerializerL2(wizcard).data

        self.response.add_data("Details", out)
        return self.response

    def Settings(self):
        modify = False
        s_obj = self.app_settings

        if 'media' in self.sender:
            if self.sender['media'].has_key('wifi_only'):
                wifi_data = self.sender['media']['wifi_only']
                if s_obj.is_wifi_data != wifi_data:
                    s_obj.is_wifi_data = wifi_data
                    modify = True

        if 'privacy' in self.sender:
            if 'invisible' in self.sender['privacy']:
                visible = not(self.sender['privacy']['invisible'])
                if s_obj.is_visible != visible:
                    s_obj.is_visible = visible
                    modify = True

            if 'dnd' in self.sender['privacy']:
                dnd = self.sender['privacy']['dnd']
                if s_obj.dnd != dnd:
                    s_obj.dnd = dnd
                    modify = True

            if 'block_unknown_req' in self.sender['privacy']:
                block_unsolicited = self.sender['privacy']['dnd']
                if s_obj.block_unsolicited != block_unsolicited:
                    s_obj.block_unsolicited = block_unsolicited
                    modify = True

            if self.sender['privacy'].has_key('public_timeline'):
                profile_private = not(self.sender['privacy']['public_timeline'])
                if s_obj.is_profile_private != profile_private:
                    s_obj.is_profile_private = profile_private
                    modify = True

        if modify:
            s_obj.save()

        return self.response

    #############OCR MessageS##############
    def OcrReqSelf(self):
        try:
            wizcard = self.user.wizcard
        except ObjectDoesNotExist:
            #this is the expected case
            wizcard = Wizcard.objects.create(user=self.user)

        c = ContactContainer.objects.create(wizcard=wizcard)

        m = BaseEntityComponent.create(
            MediaEntities,
            owner=self.user,
            is_creator=True,
            media_element="",
            media_type=MediaEntities.TYPE_IMAGE,
            media_sub_type=MediaEntities.SUB_TYPE_F_BIZCARD
        )

        local_path, remote_path = m.upload_s3(bytes(self.sender['f_ocr_card_image']))
        m.media_element = remote_path
        m.save()

        # finally connect this via related to cc
        m.related_connect(c.media)

        # Do ocr stuff
        ocr = OCR()
        result = ocr.process(local_path)
        if result.has_key('errno'):
            self.response.error_response(result)
            logging.error(result['str'])
            return self.response

        self.user.first_name = result.get('first_name', "")[:settings.MAX_NAME_LEN]
        self.user.last_name = result.get('last_name', "")[:settings.MAX_NAME_LEN]

        # wizcard.name = self.user.first_name + "" + self.user.last_name
        wizcard.email = result.get('email', "")

        wizcard.save()
        self.user.save()

        c.title = result.get('title', "")
        c.company = result.get('company', "")
        c.phone = result.get('phone', "")

        c.save()

        wc = WizcardSerializerL2(wizcard).data

        self.response.add_data("ocr_result", wc)
        logger.debug('sending OCR scan results %s', self.response)
        return self.response

    def OcrReqDeadCard(self):
        d = DeadCard.objects.create(user=self.user)
        c = ContactContainer.objects.create(wizcard=d)

        m = BaseEntityComponent.create(
            MediaEntities,
            owner=self.user,
            is_creator=True,
            media_element="",
            media_type=MediaEntities.TYPE_IMAGE,
            media_sub_type=MediaEntities.SUB_TYPE_D_BIZCARD
        )
        local_path, remote_path = m.upload_s3(bytes(self.sender['f_ocr_card_image']))
        m.media_element = remote_path
        m.save()

        m.related_connect(c.media)

        d.recognize(local_path)
        dc = DeadCardSerializerL2(d).data

        self.response.add_data("response", dc)
        return self.response

    def OcrDeadCardEdit(self):
        try:
            deadcard = DeadCard.objects.get(id=self.sender['wizcard_id'])
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        if not deadcard.activated:
            try:
                location_str = wizlib.reverse_geo_from_latlng(
                    self.app_userprofile.location.get().lat,
                    self.app_userprofile.location.get().lng
                )

            except:
                logging.error("couldn't get location for user [%s]", self.userprofile.userid)
                location_str = ""

            cctx = ConnectionContext(
                asset_obj = deadcard,
                location=location_str
            )
            deadcard.cctx = cctx

        if 'notes' in self.sender:
            deadcard.cctx.notes = self.sender['notes']['note']
            deadcard.cctx.notes_last_saved = self.sender['notes']['last_saved']
            deadcard.save()

        if self.sender.has_key('first_name'):
            deadcard.first_name = self.sender['first_name']
        if self.sender.has_key('last_name'):
            deadcard.last_name = self.sender['last_name']
        if self.sender.has_key('phone'):
            deadcard.phone = self.sender['phone']

        cc = self.sender.get('contact_container', None)
        if cc:
            cc_e = cc[0]
            d_cc = deadcard.contact_container.all()[0]

            if cc_e.has_key('phone'):
                d_cc.phone = cc_e['phone']
            if cc_e.has_key('email'):
                d_cc.email = cc_e['email']
            if cc_e.has_key('company'):
                d_cc.company = cc_e['company']
            if cc_e.has_key('title'):
                d_cc.title = cc_e['title']
            if cc_e.has_key('web'):
                d_cc.web = cc_e['web']

            d_cc.save()

        invite_other = self.sender.get('inviteother', False)
        if invite_other:
            receiver_type = "email"
            receivers = [deadcard.email]
            if receivers:
                self.do_future_user(self.user.wizcard, receiver_type, receivers)
                #send_wizcard.delay(self.user.wizcard, receivers[0], template="emailscaninvite")
                deadcard.invited = True
            else:
                self.response.error_response(err.NO_RECEIVER)
        else:
            if deadcard.activated == False:
                #send_wizcard.delay(self.user.wizcard, deadcard.email, template="emailscan")
                email_trigger.send(self.user, trigger=EmailEvent.SCANNED, source=self.user.wizcard, to_email=deadcard.email)

        # no f_bizCardEdit..for now atleast. This will always come via scan
        # or rescan
        deadcard.activated = True
        deadcard.save()

        dc = DeadCardSerializerL2(deadcard).data
        self.response.add_data("response", dc)

        return self.response

    def MeishiStart(self):
        wizcard = self.user.wizcard
        m = Meishi.objects.create(lat=self.lat, lng=self.lng, wizcard=wizcard)

        self.response.add_data("mID", m.pk)

        users, count = self.app_userprofile.lookup(
            settings.DEFAULT_MAX_MEISHI_LOOKUP_RESULTS)

        if count:
            out = UserSerializerL0(users, many=True).data
            self.response.add_data("m_nearby", out)

        return self.response

    def MeishiFind(self):
        try:
            m = Meishi.objects.get(id=self.sender['mID'])
        except:
            self.response.ignore()
            return self.response

        #Once we find a pairing we exchange wizcards
        m_res = m.check_meishi()
        if m_res:
            cctx = ConnectionContext(asset_obj=m)
            Wizcard.objects.exchange(m.wizcard, m_res.wizcard, cctx)
            out = WizcardSerializerL1(m_res.wizcard).data
            self.response.add_data("m_result", out)
        else:
            users, count = self.app_userprofile.lookup(
                settings.DEFAULT_MAX_MEISHI_LOOKUP_RESULTS)
            if count:
                out = UserSerializerL0(users, many=True).data
                self.response.add_data("m_nearby", out)

        return self.response

    def MeishiEnd(self):
        #not sure yet what to do here...lets see
        #maybe some cleanup...but shouldn't be anything we should rely on
        #too much
        return self.response


    def GetRecommendations(self):

        size = self.sender['size'] if 'size' in self.sender else settings.GET_RECO_SIZE

        # AA: Comments: BIG Overarching comment...please get into the habit
        # of (x, y) as opposed to (x,y). Its easy to detect if you use PyCharm.
        # the right side of the editor will have some color if there are any
        # PEP warnings/errors. Function name starting in uppercase is OK.

        # AA:Comments: Expose this as a model API instead of a direct filter
        # There will be more and more filtering/conditional checks/splicing
        # etc as we go forward.
        recos = UserRecommendation.objects.getRecommendations(recotarget=self.user, size=size)

        if not recos:
            if self.app_userprofile.reco_ready != 0:
                self.app_userprofile.reco_ready = 0
                self.app_userprofile.save()
            genreco.send(self.user, recotarget=self.user.id)

        self.response.add_data("recos", recos)
        return self.response

    def SetRecoAction(self):
        recoid = self.sender['reco_id'] if 'reco_id' in self.sender else None
        action = self.sender['action'] if 'action' in self.sender else None
        if not recoid or not action:
            self.response.error_response(err.INVALID_MESSAGE)
            return self.response

        recoptr = UserRecommendation.objects.get(id=recoid)
        # AA: Comments: before below if can happen, an exception will occur
        # from the get hence above has to be in try except ObjectNotFound with appropriate
        # sentry log
        if recoptr:
            try:
                recoptr.setAction(action)
            except:
                self.response.error_response(err.INVALID_RECOACTION)
        else:
            self.response.error_response(err.INVALID_RECOID)

        return self.response

    # Entity Api's for App
    def EntityCreate(self):
        e, s = BaseEntity.entity_cls_ser_from_type(entity_type=self.sender.get('entity_type'))
        entity = BaseEntityComponent.create(e, owner=self.user, is_creator=True, **self.sender)

        updated, l = entity.create_or_update_location(self.lat, self.lng)
        l.start_timer(entity.timeout)

        out = s(entity, **self.user_context).data

        self.response.add_data("result", out)
        return self.response

    def EntityDestroy(self):
        try:
            table = VirtualTable.objects.get(id=self.sender['table_id'])
        except ObjectDoesNotExist:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        if table.get_creator() == self.user:
            table.delete(type=verbs.WIZCARD_TABLE_DESTROY[0])
        else:
            self.response.error_response(err.NOT_AUTHORIZED)

        return self.response

    def EntityJoin(self):
        id = self.sender.get('entity_id')
        entity_type = self.sender.get('entity_type')

        try:
            e, s = BaseEntity.entity_cls_ser_from_type(entity_type, detail=True)
            entity = e.objects.get(id=id)
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        entity.join(self.user)

        out = s(entity, **self.user_context).data
        self.response.add_data("result", out)

        return self.response

    def EntityLeave(self):
        id = self.sender.get('entity_id')
        entity_type = self.sender.get('entity_type')

        try:
            e, s = BaseEntity.entity_cls_ser_from_type(entity_type)
            entity = e.objects.get(id=id)
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        entity.leave(self.user)

        out = s(entity, **self.user_context).data
        self.response.add_data("result", out)

        return self.response

    def EntityEdit(self):
        id = self.sender.get('entity_id')
        entity_type = self.sender.get('entity_type')

        try:
            e, s = BaseEntity.entity_cls_ser_from_type(entity_type)
            entity = e.objects.get(id=id)
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        if entity.get_creator() != self.user:
            self.response.error_response(err.NOT_AUTHORIZED)
            return self.response

        entity.name = self.sender.get('name', entity.name)

        if 'timeout' in self.sender:
            entity.timeout = self.sender['timeout']
            timeout_secs = entity.timeout*60
            entity.location.get().reset_timer(timeout_secs)

        entity.save()

        out = s(entity, **self.user_context).data
        self.response.add_data("result", out)

        return self.response

    def EventsGet(self):
        do_location = True
        if self.lat is None and self.lng is None:
            try:
                self.lat = self.app_userprofile.location.get().lat
                self.lng = self.app_userprofile.location.get().lng
            except:
                # maybe location timedout. Shouldn't happen if messages from app
                # are coming correctly...
                logger.warning('No location information available')
                do_location = False

        m_events = Event.objects.users_entities(self.user)
        n_events, count = Event.objects.lookup(
            self.lat,
            self.lng,
            settings.DEFAULT_MAX_LOOKUP_RESULTS
        ) if do_location else []

        # temp for now
        if count <= 2:
            n_events = Event.objects.all()

        events = list(set(m_events) | set(n_events))

        if events:
            events_serialized = EventSerializerL1(
                events,
                many=True,
                **self.user_context
            ).data

            self.response.add_data("result", events_serialized)

        return self.response

    def EntitiesEngage(self):
        s = set()
        # {"likes": [{'entity_type': "", 'entity_id': "", 'like_level': ""}, "views": [], "follows": []}
        if 'likes' in self.sender:
            _l = []
            for item in self.sender['likes']:
                try:
                    e = BaseEntity.objects.get(id=item['entity_id'])
                    level = item.get('like_level', EntityUserStats.MID_ENGAGEMENT_LEVEL)
                    e.engagements.like(self.user, level)
                    _l.append(e.engagements)
                except:
                    self.response.error_response(err.OBJECT_DOESNT_EXIST)
            if len(_l):
                s = s.union(_l)
        if 'views' in self.sender:
            _v = []
            for item in self.sender['views']:
                try:
                    e = BaseEntity.objects.get(id=item['entity_id'])
                    e.engagements.viewed(self.user)
                    _v.append(e.engagements)
                except:
                    self.response.error_response(err.OBJECT_DOESNT_EXIST)
            if len(_v):
                s = s.union(_v)
        if 'follows' in self.sender:
            _f = []
            for item in self.sender['follows']:
                try:
                    e = BaseEntity.objects.get(id=item['entity_id'])
                    e.engagements.follow(self.user)
                    _f.append(e.engagements)
                except:
                    self.response.error_response(err.OBJECT_DOESNT_EXIST)
            if len(_f):
                s = s.union(_f)
        if 'unfollows' in self.sender:
            _uf = []
            for item in self.sender['unfollows']:
                try:
                    e = BaseEntity.objects.get(id=item['entity_id'])
                    e.engagements.unfollow(self.user)
                    _uf.append(e.engagements)
                except:
                    self.response.error_response(err.OBJECT_DOESNT_EXIST)
            if len(_uf):
                s = s.union(_uf)

        out_list = list(s)
        ls = EntityEngagementSerializer(out_list, many=True, **self.user_context)
        self.response.add_data('result', ls.data)

        return self.response

    def EntityQuery(self):
        query_str = self.sender['query_str']
        entity_type = self.sender.get('entity_type')

        e, s = BaseEntity.entity_cls_ser_from_type(entity_type)

        result, count = e.objects.query(query_str)

        if count:
            out = s(result, many=True, **self.user_context).data
            self.response.add_data("result", out)

        self.response.add_data("count", count)

        return self.response

    def MyEntities(self):
        entity_type = self.sender.get('entity_type')
        cls, s = BaseEntity.entity_cls_ser_from_type(entity_type)

        entities = cls.objects.users_entities(self.user)

        out = s(entities, many=True, **self.user_context).data
        count = entities.count()

        if count:
            self.response.add_data("result", out)
        self.response.add_data("count", count)
        return self.response

    def EntityDetails(self):
        id = self.sender.get('entity_id')
        entity_type = self.sender.get('entity_type')
        detail = self.sender.get('detail', True)

        try:
            e, s = BaseEntity.entity_cls_ser_from_type(entity_type, detail=detail)
            entity = e.objects.get(id=id)
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        if entity.secure and not entity.is_joined(self.user):
            self.response.error_response(err.NOT_AUTHORIZED)
            return self.response

        out = s(entity, **self.user_context).data
        self.response.add_data("result", out)

        return self.response

    def TableJoinByInvite(self):
        return self.EntityJoin()

wizrequest_handler = WizRequestHandler.as_view()
#wizconnection_request = login_required(WizConnectionRequestView.as_view())
