""" .. autofunction:: wizconnection_request

.. autofunction:: wizconnection_accept

.. autofunction:: wizconnection_decline

.. autofunction:: wizconnection_cancel

.. autofunction:: wizconnection_delete

.. autofunction:: user_block

.. autofunction:: user_unblock
"""
import json
import pdb
import logging
import re
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from lib.ocr import OCR
from lib.preserialize import serialize
from django.contrib.contenttypes.models import ContentType
from wizcardship.models import WizConnectionRequest, Wizcard, ContactContainer, WizcardFlick
from notifications.models import notify, Notification
from virtual_table.models import VirtualTable, Membership
from meishi.models import Meishi
from response import Response, NotifResponse
from userprofile.models import UserProfile
from userprofile.models import AddressBook, AB_Candidate_Emails, AB_Candidate_Phones, AB_Candidate_Names, AB_User
from userprofile.models import FutureUser
from lib import wizlib, noembed
from lib.create_share import send_wizcard, create_vcard
from email_and_push_infra.models import EmailAndPush
from email_and_push_infra.signals import email_trigger
from wizcard import err
from dead_cards.models import DeadCards
from wizserver import fields
from django.utils import timezone
import random
from django.core.cache import cache
from django.conf import settings
from lib.nexmomessage import NexmoMessage
import colander
from wizcard import message_format as message_format
from wizserver import verbs
from base.cctx import ConnectionContext
from recommendation.models import UserRecommendation, Recommendation, genreco
from raven.contrib.django.raven_compat.models import client
from wizserver.tasks import contacts_upload_task
from stats.models import Stats
from converter import Converter
from django.core.files import File

now = timezone.now

logger = logging.getLogger(__name__)

class WizRequestHandler(View):
    def post(self, request, *args, **kwargs):
        self.request = request
        logger.debug(request)

        # Dispatch to appropriate message handler
        pdispatch = ParseMsgAndDispatch(self.request)
        try:
            pdispatch.dispatch()
        except:
            client.captureException()
            pdispatch.response.error_response(err.INTERNAL_ERROR)
        #send response
        return pdispatch.response.respond()

class ParseMsgAndDispatch(object):
    def __init__(self, request):
        self.request = request
        self.response = Response
        self.msg = json.loads(self.request.body)
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

        return self.headerProcess()

    def securityException(self):
        #AA TODO
        return None

    def msg_has_location(self):
        return ('lat' in self.msg['header'] and 'lng' in self.msg['header']) or ('lat' in self.msg['sender'] and 'lng' in self.msg['sender'])

    def msg_is_initial(self):
        return self.msg_type in ['phone_check_req', 'phone_check_rsp', 'login']

    def msg_is_from_wizweb(self):
        return self.device_id == settings.WIZWEB_DEVICE_ID

    def validateHeader(self):
        #hashed passwd check
        #username, userID, wizUserID, deviceID
        #is_authenticated check
        if self.msg_type not in verbs.wizcardMsgTypes:
            return False

        self.msg_id = verbs.wizcardMsgTypes[self.msg_type]
        return True

    def validateSender(self, sender):
        self.sender = sender
        if not self.msg_is_initial():
            try:
                self.user = User.objects.get(id=sender['wizUserID'])
                self.userprofile = self.user.profile
                self.user_stats, created = Stats.objects.get_or_create(user=self.user)
            except:
                logger.error('Failed User wizUserID %s, userID %s', sender['wizUserID'], sender['userID'])
                return False

            if self.userprofile.userid != self.sender['userID']:
                logger.error('Failed User wizUserID %s, userID %s', sender['wizUserID'], sender['userID'])
                return False

        #AA:TODO - Move to header
        if self.msg_has_location():
            self.lat = self.sender['lat']
            self.lng = self.sender['lng']
            logger.debug('User %s @lat, lng: {%s, %s}',
                         self.user.first_name+" "+self.user.last_name, self.lat, self.lng)

        return True

    def validateAppVersion(self):
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

    def validateWizWebMsg(self):
        if self.msg.has_key('sender'):
            self.sender = self.msg['sender']

        return True, self.response

    def validate(self):
        try:
            #self.header = message_format.CommonHeaderSchema().deserialize(self.msg['header'])
            self.header = self.msg['header']
        except colander.Invalid:
            self.response.ignore()
            return False, self.response

        self.msg_type = self.header['msgType']
        self.device_id = self.header['deviceID']

        if self.msg_is_from_wizweb():
            return self.validateWizWebMsg()

        logger.debug('received message %s', self.msg_type)
        logger.debug('%s', self)

        if not self.validateHeader():
            self.securityException()
            self.response.ignore()
            logger.warning('user failed header security check on msg {%s}', \
                           self.msg_type)
            return False, self.response

        if not self.validateAppVersion():
            self.response.error_response(err.VERSION_UPGRADE)
            return False, self.response

        if self.msg.has_key('sender') and not self.validateSender(self.msg['sender']):
            self.securityException()
            self.response.ignore()
            logger.warning('user failed sender security check on msg {%s}', \
                           self.msg_type)
            return False, self.response
        if 'receiver' in self.msg:
            self.receiver = self.msg['receiver']

        #AA:TODO: App to fix - This has to be in header
        self.on_wifi = self.sender['onWifi'] if \
            self.sender.has_key('onWifi') else False

        return True, self.response

    def headerProcess(self):

        VALIDATOR = 0
        HANDLER = 1
        STATS = 2

        msgTypesValidatorsAndHandlers = {
            # wizweb messages
            verbs.MSG_WIZWEB_QUERY_USER:
                (
                    message_format.WizWebUserQuerySchema,
                    self.WizWebUserQuery,
                    None
                ),
            verbs.MSG_WIZWEB_QUERY_WIZCARD:
                (
                    message_format.WizWebWizcardQuerySchema,
                    self.WizWebWizcardQuery,
                    None
                ),
            verbs.MSG_WIZWEB_CREATE_USER:
                (
                    message_format.WizWebUserCreateSchema,
                    self.WizWebUserCreate,
                    None
                ),
            verbs.MSG_WIZWEB_ADD_EDIT_CARD:
                (
                    message_format.WizWebAddEditCardSchema,
                    self.WizWebAddEditCard,
                    None
                ),
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
            verbs.MSG_TABLE_QUERY:
                (
                    message_format.TableQuerySchema,
                    self.TableQuery,
                    None,
                ),
            verbs.MSG_MY_TABLES:
                (
                    message_format.TableMyTablesSchema,
                    self.TableMyTables,
                    None
                ),
            verbs.MSG_TABLE_SUMMARY:
                (
                    message_format.TableSummarySchema,
                    self.TableSummary,
                    None,
                ),
            verbs.MSG_TABLE_DETAILS:
                (
                    message_format.TableDetailsSchema,
                    self.TableDetails,
                    None,
                ),
            verbs.MSG_CREATE_TABLE:
                (
                    message_format.TableCreateSchema,
                    self.TableCreate,
                    None,
                ),
            verbs.MSG_JOIN_TABLE:
                (
                    message_format.TableJoinSchema,
                    self.TableJoin,
                    None,
                ),
            verbs.MSG_LEAVE_TABLE:
                (
                    message_format.TableLeaveSchema,
                    self.TableLeave,
                    None
                ),
            verbs.MSG_DESTROY_TABLE:
                (
                    message_format.TableDestroySchema,
                    self.TableDestroy,
                    None,
                ),
            verbs.MSG_TABLE_EDIT:
                (
                    message_format.TableEditSchema,
                    self.TableEdit,
                    None
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
            verbs.MSG_EMAIL_TEMPLATE:
                (
                    message_format.GetEmailTemplateSchema,
                    self.GetEmailTemplate,
                    Stats.objects.inc_email_template,
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
                )
        }
        #update location since it may have changed
        if self.msg_has_location() and not self.msg_is_initial():
            self.userprofile.create_or_update_location(
                self.lat,
                self.lng)

        # process
        response = msgTypesValidatorsAndHandlers[self.msg_id][HANDLER]()

        # bump stats
        if msgTypesValidatorsAndHandlers[self.msg_id][STATS]:
            msgTypesValidatorsAndHandlers[self.msg_id][STATS](self.user_stats, self.global_stats)

        self.headerPostProcess()
        return response

    def headerPostProcess(self):
        #make the user as alive
        if not (self.msg_is_initial() or self.msg_is_from_wizweb()):
            self.userprofile.online()

    def PhoneCheckRequest(self):
        device_id = self.header['deviceID']
        username = self.sender['username']
        response_mode = self.sender['responseMode']
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
        device_id = self.header['deviceID']
        challenge_response = self.sender['responseKey']

        if not (username and challenge_response):
            self.response.error_response( \
                err.PHONE_CHECK_CHALLENGE_RESPONSE_DENIED)
            return self.response

        k_user = (settings.PHONE_CHECK_USER_KEY % username)
        k_rand = (settings.PHONE_CHECK_USER_RAND_KEY % username)
        k_retry = (settings.PHONE_CHECK_USER_RETRY_KEY % username)
        k_device_id = (settings.PHONE_CHECK_DEVICE_ID_KEY % username)

        d = cache.get_many([k_user, k_device_id, k_rand, k_retry])
        logger.info( "cached value for phone_check_xx {%s}", d)

        if not (d.has_key(k_user) and \
                        d.has_key(k_rand) and \
                        d.has_key(k_retry) and \
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

        #response is valid. create user here and send back userID
        user, created = User.objects.get_or_create(username=username)

        if created:
            #AA TODO: Generate hash from deviceID and user.pk
            #and maybe phone number
            password = UserProfile.objects.gen_password(user.pk, device_id)
            user.set_password(password)
            #generate internal userid
            user.save()
        else:
            if device_id != user.profile.device_id:
                #device_id is part of password, reset password to reflect new deviceID
                password = UserProfile.objects.gen_password(user.pk,
                                                            device_id)
                user.set_password(password)
                user.save()

            # mark for sync if profile is activated
            if user.profile.activated:
                user.profile.do_sync = True

        user.profile.device_id = device_id

        #all done. #clear cache
        cache.delete_many([k_user, k_device_id, k_rand, k_retry])

        user.profile.save()

        self.response.add_data("userID", user.profile.userid)
        return self.response

    def Login(self):
        try:
            self.username = self.sender['username']
            self.user = User.objects.get(username=self.username)
            self.password = self.device_id
            auth = authenticate(username=self.username, password=self.password)
            if auth is None:
                #invalid password
                self.response.error_response(err.AUTHENTICATION_FAILED)
                return self.response

            self.response.add_data("wizUserID", self.user.pk)
        except:
            self.securityException()
            self.response.ignore()

        return self.response

    def Register(self):
        #fill in device details
        try:
            self.userprofile.device_type = self.sender['deviceType']
        except:
            pass

        self.userprofile.reg_token = self.sender['reg_token']

        if self.userprofile.do_sync:
            #sync all syncables
            s = self.userprofile.do_resync()
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
            self.userprofile.do_sync = False
        self.userprofile.save()

        return self.response

    def LocationUpdate(self):
        #update location in ptree
        self.userprofile.create_or_update_location(self.lat, self.lng)
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
                d['wizUserID'] = wizcard.user_id
                if Wizcard.objects.are_wizconnections(
                        self.user.wizcard,
                        wizcard):
                    d['tag'] = "connected"
                else:
                    d['tag'] = "other"

                wc = Wizcard.objects.serialize(wizcard,
                                               template=fields.wizcard_template_brief)
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
                d['wizUserID'] = wizcard.user_id
                if Wizcard.objects.are_wizconnections(
                        self.user.wizcard,
                        wizcard):
                    d['tag'] = "connected"
                elif self.user == wizcard.user:
                    d['tag'] = "own"
                else:
                    d['tag'] = "other"

                wc = Wizcard.objects.serialize(wizcard,
                                               template=fields.wizcard_template_brief)
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

        if self.sender.has_key('recoActions'):

            recoactions = self.sender['recoActions']

            for rectuple in recoactions:

                recid = rectuple['recoID']
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
        flicked_wizcards, count = WizcardFlick.objects.lookup(
            self.user.pk,
            self.lat,
            self.lng,
            settings.DEFAULT_MAX_LOOKUP_RESULTS)
        if count:
            notifResponse.notifFlickedWizcardsLookup(count,
                                                     self.user, flicked_wizcards)

        users, count = self.userprofile.lookup(
            self.user.pk,
            settings.DEFAULT_MAX_LOOKUP_RESULTS)
        if count:
            notifResponse.notifUserLookup(
                count,
                self.user,
                users)

        reco_count = self.userprofile.reco_ready
        if reco_count:
            self.userprofile.reco_ready = 0

        tables, count = VirtualTable.objects.lookup(
            self.user.pk,
            self.lat,
            self.lng,
            settings.DEFAULT_MAX_LOOKUP_RESULTS)
        if count:
            notifResponse.notifTableLookup(count, self.user, tables)

        Notification.objects.mark_specific_as_read(notifications)

        #tickle the timer to keep it going and update the location if required
        self.userprofile.create_or_update_location(self.lat, self.lng)

        self.response = notifResponse
        return self.response

    def RolodexEdit(self):
        wizcard1 = self.user.wizcard
        try:
            wizcard2 = Wizcard.objects.get(id=self.receiver['wizCardID'])
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
        userprofile_modify = False

        wizcard, created = Wizcard.objects.get_or_create(user=self.user)
        if created:
            ContactContainer.objects.create(wizcard=wizcard)
            # set activated to true.
            self.userprofile.activated = True
            userprofile_modify = True

        #AA:TODO: Change app to call this phone as well
        if 'phone' in self.sender or 'phone1' in self.sender:
            phone = self.sender['phone'] if self.sender.has_key('phone') else self.sender['phone1']

            if wizcard.phone != phone:
                wizcard.phone = phone
                modify = True

        if 'first_name' in self.sender:
            first_name = self.sender['first_name']
            if wizcard.first_name != first_name:
                wizcard.first_name = first_name
                self.user.first_name = self.sender['first_name']
                modify = True
                user_modify = True

        if 'last_name' in self.sender:
            last_name = self.sender['last_name']
            if wizcard.last_name != last_name:
                wizcard.last_name = last_name
                self.user.last_name = self.sender['last_name']
                modify = True
                user_modify = True

        if 'email' in self.sender:
            email = self.sender['email']
            if wizcard.email != email:
                wizcard.email = email
                modify = True

        if 'thumbnailImage' in self.sender and \
                self.sender['thumbnailImage']:
            b64image = bytes(self.sender['thumbnailImage'])
            rawimage = b64image.decode('base64')
            upfile = SimpleUploadedFile("%s-%s.jpg" % \
                                        (wizcard.pk, now().strftime("%Y-%m-%d %H:%M")),
                                        rawimage, "image/jpeg")
            wizcard.thumbnailImage.save(upfile.name, upfile)
            modify = True

        if 'videoUrl' in self.sender:
            wizcard.videoUrl = self.sender['videoUrl']
            modify = True

        if 'videoThumbnailUrl' in self.sender:
            wizcard.videoThumbnailUrl = self.sender['videoThumbnailUrl']
            modify = True

        if 'extFields' in self.sender and self.sender['extFields']:
            wizcard.extFields = self.sender['extFields'].copy()
            modify = True

        if 'contact_container' in self.sender:
            contact_container_list = self.sender['contact_container']

            cc = wizcard.contact_container.all()[0]

            modify = True

            for count, contactItem in enumerate(contact_container_list):
                if 'title' in contactItem:
                    cc.title = contactItem['title']
                if 'company' in contactItem:
                    cc.company = contactItem['company']
                if 'phone' in contactItem:
                    cc.phone = contactItem['phone']

                cc.save()
                if 'f_bizCardImage' in contactItem and contactItem['f_bizCardImage']:
                    #AA:TODO: Remove try
                    try:
                        b64image = bytes(contactItem['f_bizCardImage'])
                        rawimage = b64image.decode('base64')
                        #AA:TODO: better file name
                        upfile = SimpleUploadedFile("%s-f_bc.%s.%s.jpg" % \
                                                    (wizcard.pk, cc.pk, now().strftime \
                                                        ("%Y-%m-%d %H:%M")), rawimage, \
                                                    "image/jpeg")
                        cc.f_bizCardImage.save(upfile.name, upfile)
                    except:
                        pass

        # check if futureUser states exist for this phone or email
        # check if futureUser states exist for this phone or email
        future_users = FutureUser.objects.check_future_user(
            wizcard.email,
            wizcard.phone)
        for f in future_users:
            f.generate_self_invite(self.user)

        if future_users.count():
            future_users.delete()

        # flood to contacts
        if user_modify:
            self.user.save()
        if userprofile_modify:
            self.userprofile.save()
        if modify:
            wizcard.save()
            wizcard.flood()

        # Check for admin user connection and create it
        admin_user = UserProfile.objects.get_admin_user()
        admin_conn = wizcard.get_relationship(admin_user.wizcard)

        if not admin_conn:
            # connect implicitly with admin wizcard

            try:
                location_str = wizlib.reverse_geo_from_latlng(
                    self.userprofile.location.get().lat,
                    self.userprofile.location.get().lng
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

        #create_template.delay(wizcard)
        vcard = create_vcard(wizcard)
        if vcard:
            wizcard.save_vcard(vcard)
        if created:
            email_trigger.send(self.user,trigger=EmailAndPush.NEWUSER, wizcard=self.user.wizcard, to_email=wizcard.email)

        self.response.add_data("wizCardID", wizcard.pk)
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
                wizcard2 = Wizcard.objects.get(id=self.receiver['wizCardID'])
                self.r_user = User.objects.get(id=self.receiver['wizUserID'])
            except:
                self.r_user = User.objects.get(id=self.receiver['wizUserID'])
                wizcard2 = self.r_user.wizcard

        except KeyError:
            self.securityException()
            self.securityException()
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
                    wizCardID=wizcard2.id)
            )
            self.response.add_data("status", status)
            return self.response

        if flag == "reaccept" or flag == "unarchive":
            # add-to-rolodex case. Happens when user had previously declined/deleted this guy
            try:
                location_str = wizlib.reverse_geo_from_latlng(
                    self.userprofile.location.get().lat,
                    self.userprofile.location.get().lng
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
                 wizCardID=wizcard2.id)
        )
        self.response.add_data("status", status)
        genreco.send(self.user, recotarget=self.user.id)
        return self.response

    def WizConnectionRequestDecline(self):
        try:
            wizcard1 = self.user.wizcard
            wizcard2 = Wizcard.objects.get(id=self.receiver['wizCardID'])
        except KeyError:
            self.securityException()
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
            wizcards = self.receiver['wizCardIDs']

            for w in wizcards:
                try:
                    w_id = w.get("wizCardID")
                    dead_card = w.get("dead_card")
                except:
                    self.response.error_response(err.INVALID_MESSAGE)
                    return self.response

                if dead_card:
                    try:
                        wizcard2 = DeadCards.objects.get(id=w_id)
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
            self.securityException()
            self.response.ignore()

        return self.response

    def WizcardRolodexArchivedCards(self):
        try:
            wizcard = self.user.wizcard
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        a_wc = wizcard.get_deleted()
        self.response.add_data("wizcards", Wizcard.objects.serialize(a_wc, fields.wizcard_template_full))
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
                self.lat = self.userprofile.location.get().lat
                self.lng = self.userprofile.location.get().lng
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
            self.securityException()
            self.response.ignore()
            return self.response
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

    def WizcardMyFlicks(self):
        self.wizcard = Wizcard.objects.get(id=self.sender['wizCardID'])
        my_flicked_cards = self.wizcard.flicked_cards.exclude(expired=True)

        count = my_flicked_cards.count()
        if count:
            flicks_s = WizcardFlick.objects.serialize(
                my_flicked_cards,
                fields.my_flicked_wizcard_template)
            self.response.add_data("queryResult", flicks_s)
        self.response.add_data("count", count)

        return self.response

    def WizcardFlickWithdraw(self):
        try:
            self.flicked_card = WizcardFlick.objects.get(id=self.sender['flickCardID'])
        except KeyError:
            self.securityException()
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
            self.securityException()
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
            self.securityException()
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
            self.securityException()
            self.response.ignore()
            return self.response

        try:
            flicked_card = WizcardFlick.objects.get(id=flick_id)
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        if flicked_card.wizcard.user != self.user:
            self.securityException()
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
            asset_type = self.sender['assetType']
            sender_id = self.sender['assetID']
            receiver_type = self.receiver['receiverType']
            receivers = self.receiver['receiverIDs']
        except:
            self.securityException()
            self.response.ignore()
            return self.response

        if asset_type == "wizcard":
            try:
                wizcard = Wizcard.objects.get(id=sender_id)
            except ObjectDoesNotExist:
                self.response.error_response(err.OBJECT_DOESNT_EXIST)
                return self.response

            if self.user.wizcard.id != wizcard.id:
                self.securityException()
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
            if not((table.is_secure() and table.creator == self.user) or
                       ((not table.is_secure()) and table.is_member(self.user))):
                self.response.error_response(err.NOT_AUTHORIZED)
                return self.response

            self.response = self.WizcardSendTableToXYZ(
                table,
                receiver_type,
                receivers)
        else:
            self.securityException()
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
                    self.userprofile.location.get().lat,
                    self.userprofile.location.get().lng
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
                    #create wizcard1->wizcard2
                    rel12 = Wizcard.objects.cardit(wizcard,
                                                   r_wizcard,
                                                   status=verbs.PENDING,
                                                   cctx=cctx1)
                #Q notif for to_wizcard
                if to_notify:
                    notify.send(
                        self.user, recipient=r_user,
                        verb=verbs.WIZREQ_T[0] if receiver_type == verbs.INVITE_VERBS[verbs.WIZCARD_CONNECT_T] else
                        conn_status,
                        target=wizcard,
                        action_object=rel12)


                #Context should always have the from_wizcard and for the time being sender's location - Still debating
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
                    wizCardID=r_wizcard.id)
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
            #receiverIDs has wizUserIDs
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
        numreceivers = len(receivers)
        for r in receivers:
            # for a typed out email/sms, the user may still be in wiz
            wizcard = UserProfile.objects.check_user_exists(receiver_type, r)

            if wizcard:
                # If there are more 1 receiver, its ok to fail silently otherwise throw an error
                if numreceivers == 1 and self.user.wizcard.id == wizcard.id:
                    self.response.error_response(err.SELF_INVITE)
                    return self.response

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
                        #Q notif for to_wizcard
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
                    email_trigger.send(self.user, trigger=EmailAndPush.INVITED, wizcard=self.user.wizcard, to_email=r)
                    #send_wizcard.delay(self.user.wizcard, r)

            else:
                FutureUser.objects.get_or_create(
                        inviter=self.user,
                        content_type=ContentType.objects.get_for_model(obj),
                        object_id=obj.id,
                        phone=r if receiver_type == verbs.INVITE_VERBS[verbs.SMS_INVITE] else "",
                        email=r if receiver_type == verbs.INVITE_VERBS[verbs.EMAIL_INVITE] else ""
                )
                if receiver_type == verbs.INVITE_VERBS[verbs.EMAIL_INVITE]:
                    email_trigger.send(self.user, trigger=EmailAndPush.INVITED, wizcard=self.user.wizcard, to_email=r)
                    #send_wizcard.delay(self.user.wizcard, r)

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
        #send back to app for selection

        if count:
            users_s = UserProfile.objects.serialize_split(
                self.user,
                map(lambda x: x.user, result))
            self.response.add_data("queryResult", users_s)
        self.response.add_data("count", count)

        return self.response

    def GetCommonConnections(self):
        MAX_L1_LIST_VIEW = 3


        try:
            wizcard1 = Wizcard.objects.get(id=self.sender['wizCardID'])
            wizcard2 = Wizcard.objects.get(id=self.receiver['wizCardID'])
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
            common_s = Wizcard.objects.serialize(common[:split], fields.wizcard_template_brief)
            self.response.add_data("wizcards", common_s)
        self.response.add_data("total", count)

        return self.response

    def GetVideoThumbnailUrl(self):
        videoUrl = self.sender['videoUrl']

        try:
            resp = noembed.embed(videoUrl)
            videoThumbnailUrl = resp.thumbnail_url
        except:
            # Try with ffmpeg
            VIDEO_SEEK_SECONDS = 5
            OUTFILE_PATH = "/tmp/"
            videoUrl = self.sender['videoUrl']
            rand_val = random.randint(settings.PHONE_CHECK_RAND_LOW, settings.PHONE_CHECK_RAND_HI)

            filename = "thumbnail_video-%s.%s.jpg" % (rand_val, now().strftime ("%Y-%m-%d %H:%M"))
            outfile = OUTFILE_PATH+filename

            c = Converter()
            try:
                c.thumbnail(videoUrl, VIDEO_SEEK_SECONDS, outfile, size='160:120')
            except:
                self.response.error_response(err.EMBED_FAILED)
                return self.response

            # upload file to aws and get url
            remote_path = '/thumbnails/' + filename

            try:
                videoThumbnailUrl = wizlib.uploadtoS3(outfile, remote_dir=remote_path)
            except:
                self.response.error_response(err.EMBED_FAILED)
                return self.response

        self.response.add_data("videoThumbnailUrl", videoThumbnailUrl)
        return self.response

    def TableQuery(self):
        if not self.receiver.has_key('name'):
            self.securityException()
            self.response.ignore()
            return self.response

        result, count = VirtualTable.objects.query_tables(self.receiver['name'])

        if count:
            tables_s = VirtualTable.objects.serialize_split(result,
                                                            self.user,
                                                            fields.nearby_table_template)
            self.response.add_data("queryResult", tables_s)
        self.response.add_data("count", count)

        return self.response

    def TableMyTables(self):
        tables = self.user.tables.exclude(expired=True)
        count = tables.count()
        if count:
            tables_s = VirtualTable.objects.serialize(tables, fields.table_template)
            self.response.add_data("queryResult", tables_s)
        self.response.add_data("count", count)
        return self.response

    def TableSummary(self):
        table = VirtualTable.objects.get(id=self.sender['tableID'])
        if table.is_secure() and not table.is_member(self.user):
            self.response.error_response(err.NOT_AUTHORIZED)
            return self.response

        out = table.serialize(fields.nearby_table_template)
        self.response.add_data("Summary", out)
        return self.response

    def TableDetails(self):
        #get the members
        table = VirtualTable.objects.get(id=self.sender['tableID'])
        if table.is_secure() and not table.is_member(self.user):
            self.response.error_response(err.NOT_AUTHORIZED)
            return self.response

        members = table.users.all()
        count = members.count()
        if count:
            out = UserProfile.objects.serialize_split(self.user, members)
            self.response.add_data("Members", out)
            self.response.add_data("Count", count)
            self.response.add_data("CreatorID", table.creator.id)

        return self.response

    def WizcardGetDetail(self):
        try:
            wizcard = Wizcard.objects.get(id=self.receiver['wizCardID'])
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response
        r_userprofile = wizcard.user.profile

        if r_userprofile.is_profile_private:
            template = fields.wizcard_template_brief
        else:
            template = fields.wizcard_template_full

        out = Wizcard.objects.serialize(wizcard, template)
        self.response.add_data("Details", out)
        return self.response

    def TableCreate(self):
        tablename = self.sender['table_name']
        secure = self.sender['secureTable']
        if self.sender.has_key('timeout'):
            timeout = self.sender['timeout'] if self.sender['timeout'] else settings.WIZCARD_DEFAULT_TABLE_LIFETIME
        else:
            timeout = settings.WIZCARD_DEFAULT_TABLE_LIFETIME

        if secure:
            password = self.sender['password']
        else:
            password = ""

        a_created = self.sender['created']

        table = VirtualTable.objects.create(tablename=tablename, secureTable=secure,
                                            password=password, creator=self.user,
                                            a_created = a_created, timeout=timeout)
        table.inc_numsitting()

        #TODO: AA handle create failure and/or unique name enforcement
        Membership.objects.get_or_create(user=self.user, table=table)
        #AA:TODO move create to overridden create in VirtualTable

        #update location in ptree
        table.create_location(self.lat, self.lng)
        l = table.location.get()
        l.start_timer(timeout)
        table.save()
        self.response.add_data("tableID", table.pk)
        return self.response

    def TableJoinByInvite(self):
        return self.TableJoin(skip_password=True)

    def TableJoin(self, skip_password=False):
        try:
            table = VirtualTable.objects.get(id=self.sender['tableID'])
        except ObjectDoesNotExist:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        if self.user is table.creator:
            self.response.error_response(err.EXISTING_MEMBER)
            return self.response

        if table.is_secure() and not skip_password:
            password = self.sender['password']
        else:
            password = None

        joined = table.join_table_and_exchange(self.user, password, skip_password)

        if joined is None:
            self.response.error_response(err.AUTHENTICATION_FAILED)
        else:
            self.response.add_data("tableID", joined.pk)
        return self.response

    def TableLeave(self):
        try:
            table = VirtualTable.objects.get(id=self.sender['tableID'])
            leave = table.leave_table(self.user)
            self.response.add_data("tableID", leave.pk)
        except:
            pass

        return self.response


    def TableDestroy(self):
        try:
            table = VirtualTable.objects.get(id=self.sender['tableID'])
        except ObjectDoesNotExist:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        if table.creator == self.user:
            table.delete(type=verbs.WIZCARD_TABLE_DESTROY[0])
        else:
            self.response.error_response(err.NOT_AUTHORIZED)

        return self.response


    def TableEdit(self):
        try:
            table_id = self.sender['tableID']
        except KeyError:
            self.securityException()
            self.response.ignore()
            return self.response
        try:
            table = VirtualTable.objects.get(id=table_id)
        except ObjectDoesNotExist:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        if table.creator != self.user:
            self.response.error_response(err.NOT_AUTHORIZED)
            return self.response

        if self.sender.has_key('oldName') and self.sender.has_key('newName'):
            old_name = self.sender['oldName']
            new_name = self.sender['newName']

            if old_name != table.tablename:
                self.response.error_response(err.NAME_ERROR)
                return self.response

            table.tablename = new_name
        if self.sender.has_key('timeout'):
            timeout = self.sender['timeout']*60
            a_created = self.sender['created']
            table.a_created = a_created
            table.location.get().reset_timer(timeout)
        table.save()

        self.response.add_data("tableID", table.pk)
        return self.response

    def Settings(self):
        modify = False

        if 'media' in self.sender:
            if self.sender['media'].has_key('wifiOnly'):
                wifi_data = self.sender['media']['wifiOnly']
                if self.userprofile.is_wifi_data != wifi_data:
                    self.userprofile.is_wifi_data = wifi_data
                    modify = True

        if 'privacy' in self.sender:
            if 'invisible' in self.sender['privacy']:
                visible = not(self.sender['privacy']['invisible'])
                if self.userprofile.is_visible != visible:
                    self.userprofile.is_visible = visible
                    modify = True

            if 'dnd' in self.sender['privacy']:
                dnd = self.sender['privacy']['dnd']
                if self.userprofile.dnd != dnd:
                    self.userprofile.dnd = dnd
                    modify = True

            if 'block_unknown_req' in self.sender['privacy']:
                block_unsolicited = self.sender['privacy']['dnd']
                if self.userprofile.block_unsolicited != block_unsolicited:
                    self.userprofile.block_unsolicited = block_unsolicited
                    modify = True

            if self.sender['privacy'].has_key('publicTimeline'):
                profile_private = not(self.sender['privacy']['publicTimeline'])
                if self.userprofile.is_profile_private != profile_private:
                    self.userprofile.is_profile_private = profile_private
                    modify = True

        if modify:
            self.userprofile.save()

        return self.response

    #############OCR MessageS##############
    def OcrReqSelf(self):
        try:
            wizcard = self.user.wizcard
        except ObjectDoesNotExist:
            #this is the expected case
            wizcard = Wizcard(user=self.user)
            #AR: Temporary Fix, ideally we should be sending only the OCR response without creating
            # Wizcard. Want to be sure about the implications
            self.userprofile.activated = True
            self.userprofile.save()
            wizcard.save()

        c = ContactContainer.objects.create(wizcard=wizcard)

        if self.sender.has_key('f_ocrCardImage'):
            b64image = bytes(self.sender['f_ocrCardImage'])
            rawimage = b64image.decode('base64')
            #AA:TODO maybe time to put this in lib
            upfile = SimpleUploadedFile("%s-%s.jpg" % \
                                        (wizcard.pk, now().strftime("%Y-%m-%d %H:%M")),
                                        rawimage, "image/jpeg")

            c.f_bizCardImage.save(upfile.name, upfile)
            path = c.f_bizCardImage.local_path()
        else:
            self.response.ignore()
            return self.response

        #Do ocr stuff
        ocr = OCR()
        result = ocr.process(path)
        if result.has_key('errno'):
            self.response.error_response(result)
            logging.error(result['str'])
            return self.response

        if result.has_key('first_name') and result.get('first_name'):
            wizcard.first_name = result.get('first_name')
            self.user.first_name = wizcard.first_name
        if result.has_key('last_name') and result.get('last_name'):
            wizcard.last_name = result.get('last_name')
            self.user.last_name = wizcard.last_name
        if result.has_key('email') and result.get('email'):
            wizcard.email = result.get('email')

        wizcard.save()
        self.user.save()

        if result.has_key('title') and result.get('title'):
            c.title = result.get('title')
        if result.has_key('company') and result.get('company'):
            c.company = result.get('company')
        if result.has_key('phone') and result.get('phone'):
            c.phone = result.get('phone')
        c.end="current"
        c.save()

        wc = wizcard.serialize()

        self.response.add_data("ocr_result", wc)
        logger.debug('sending OCR scan results %s', self.response)
        return self.response

    def OcrReqDeadCard(self):
        try:
            wizcard = self.user.wizcard
        except ObjectDoesNotExist:
            self.response.error_response(err.CRITICAL_ERROR)
            return self.response

        d = DeadCards.objects.create(user=self.user)

        if self.sender.has_key('f_ocrCardImage'):
            b64image = bytes(self.sender['f_ocrCardImage'])
            rawimage = b64image.decode('base64')
        else:
            self.response.ignore()
            return self.response

        upfile = SimpleUploadedFile("%s-%s.jpg" % \
                                    (wizcard.pk, now().strftime("%Y-%m-%d %H:%M")),
                                    rawimage, "image/jpeg")
        d.f_bizCardImage.save(upfile.name, upfile)
        d.recognize()
        self.response.add_data("response", d.serialize())
        return self.response

    def OcrDeadCardEdit(self):
        if not self.sender.has_key('deadCardID'):
            self.response.error_response(err.INVALID_MESSAGE)
            return self.response
        try:
            deadcard = DeadCards.objects.get(id=self.sender['deadCardID'])
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        if not deadcard.activated:
            try:
                location_str = wizlib.reverse_geo_from_latlng(
                    self.userprofile.location.get().lat,
                    self.userprofile.location.get().lng
                )

            except:
                logging.error("couldn't get location for user [%s]", self.userprofile.userid)
                location_str = ""
            cctx = ConnectionContext(
                asset_obj = deadcard,
                location=location_str
            )
            deadcard.set_context(cctx)

        if 'notes' in self.sender:
            deadcard.cctx.notes = self.sender['notes']['note']
            deadcard.cctx.notes_last_saved = self.sender['notes']['last_saved']
            deadcard.save()

        if self.sender.has_key('first_name'):
            deadcard.first_name = self.sender['first_name']
        if self.sender.has_key('last_name'):
            deadcard.last_name = self.sender['last_name']
        inviteother = self.sender.get('inviteother', False)
        if self.sender.has_key('phone'):
            deadcard.phone = self.sender['phone']

        cc = self.sender.get('contact_container', None)
        if cc:
            cc_e = cc[0]

            if cc_e.has_key('phone'):
                deadcard.phone = cc_e['phone']
            if cc_e.has_key('email'):
                deadcard.email = cc_e['email']
            if cc_e.has_key('company'):
                deadcard.company = cc_e['company']
            if cc_e.has_key('title'):
                deadcard.title = cc_e['title']
            if cc_e.has_key('web'):
                deadcard.web = cc_e['web']

        if inviteother:
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
                email_trigger.send(self.user, trigger=EmailAndPush.SCANNED, wizcard=self.user.wizcard, to_email=deadcard.email)

        # no f_bizCardEdit..for now atleast. This will always come via scan
        # or rescan
        deadcard.activated = True
        deadcard.save()

        return self.response

    def MeishiStart(self):
        lat = self.sender['lat']
        lng = self.sender['lng']
        wizcard = self.user.wizcard
        m = Meishi.objects.create(lat=lat, lng=lng, wizcard=wizcard)

        self.response.add_data("mID", m.pk)

        users, count = self.userprofile.lookup(
            self.user.pk,
            settings.DEFAULT_MAX_MEISHI_LOOKUP_RESULTS)
        if count:
            out = UserProfile.objects.serialize(
                users,
                fields.wizcard_template_brief)
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
            #AA:Comments: can send a smaller serilized output
            #wizcard_template_full is not required. All the app needs is
            #wizcard_id, f_bizCardUrl
            out = Wizcard.objects.serialize(
                m_res.wizcard,
                template = fields.wizcard_template_brief)
            self.response.add_data("m_result", out)
        else:
            users, count = self.userprofile.lookup(
                self.user.pk,
                settings.DEFAULT_MAX_MEISHI_LOOKUP_RESULTS)
            if count:
                out = UserProfile.objects.serialize(
                    users,
                    fields.wizcard_template_brief)
                self.response.add_data("m_nearby", out)

        return self.response

    def MeishiEnd(self):
        #not sure yet what to do here...lets see
        #maybe some cleanup...but shouldn't be anything we should rely on
        #too much
        return self.response

    def GetEmailTemplate(self):
        wizcard = self.user.wizcard

        #if not wizcard.emailTemplate:
        #    create_template.delay(wizcard)

        #email = wizcard.emailTemplate.remote_url()
        #self.response.add_data("emailTemplate", email)

        return self.response



    #################WizWeb Message handling########################
    def WizWebUserQuery(self):
        if self.sender.has_key('username'):
            try:
                self.user = User.objects.get(username=self.sender['username'])
                self.wizcard = self.user.wizcard
                self.response.add_data("userID", self.user.profile.userid)
            except:
                pass
        elif self.sender.has_key('email'):
            try:
                self.wizcard = Wizcard.objects.get(email=self.sender['email'])
                self.user = self.wizcard.user
                self.response.add_data("userID", self.user.profile.userid)
            except:
                pass
        else:
            self.response.error_response(err.INVALID_MESSAGE)
            return self.response

        return self.response

    def WizWebWizcardQuery(self):
        userID = self.sender.get('userID', None)

        if not userID:
            self.response.error_response(err.INVALID_MESSAGE)
            return self.response

        if self.sender.has_key('username'):
            try:
                self.user = User.objects.get(username=self.sender['username'])
                self.wizcard = self.user.wizcard
            except:
                return self.response.error_response(err.OBJECT_DOESNT_EXIST)
        elif self.sender.has_key('email'):
            try:
                self.wizcard = Wizcard.objects.get(email=self.sender['email'])
                self.user = self.wizcard.user
            except:
                self.response.error_response(err.USER_DOESNT_EXIST)
                return self.response
        else:
            self.response.error_response(err.INVALID_MESSAGE)
            return self.response

        if self.user.profile.userid != userID:
            self.response.error_response(err.INVALID_MESSAGE)
            return self.response

        out = self.wizcard.serialize()
        self.response.add_data("result", out)
        return self.response


    def WizWebUserCreate(self):
        username = self.sender['username']
        first_name = self.sender['first_name']
        last_name = self.sender['last_name']

        if User.objects.filter(username=username).exists():
            #wizweb should have sent user query
            return self.response.error_response(err.VALIDITY_CHECK_FAILED)

        self.user = User.objects.create(username=username,
                                        first_name=first_name,
                                        last_name=last_name)

        self.user.profile.activated = False
        self.user.profile.save()
        self.response.add_data("userID", self.user.profile.userid)

        return self.response

    def WizWebAddEditCard(self):
        EDIT_LATEST = 1
        EDIT_FORCE = 2

        flood = False
        username = self.sender['username']
        userID = self.sender['userID']
        mode = self.sender.get('mode', EDIT_LATEST)

        try:
            self.user = User.objects.get(username=username)
        except:
            self.response.error_response(err.USER_DOESNT_EXIST)
            return self.response

        if self.user.profile.userid != userID:
            self.response.error_response(err.VALIDITY_CHECK_FAILED)
            return self.response

        try:
            first_name = self.sender['first_name']
            last_name = self.sender['last_name']
            phone = self.sender['phone']
            media_url = self.sender.get('mediaUrl', None)
            contact_container = self.sender['contact_container']
        except:
            self.response.error_response(err.INVALID_MESSAGE)
            return self.response

        if hasattr(self.user, 'wizcard'):
            #already existing user/wizcard
            flood = True
            wizcard = self.user.wizcard
            #AA_TODO: cross check phone

            #Add to contact container or force add depending on mode
            if mode == EDIT_FORCE:
                #delete existing contact container for this wizcard
                wizcard.contact_container.all().delete()
        else:
            #create new wizcard
            wizcard = Wizcard(user=self.user,
                              first_name=first_name,
                              last_name=last_name,
                              phone=phone)
            wizcard.save()

            #Future user handling
            future_users = FutureUser.objects.check_future_user(
                wizcard.email,
                wizcard.phone)
            for f in future_users:
                f.generate_self_invite(self.user)

            if future_users.count():
                future_users.delete()

        for c in contact_container:
            t_row = ContactContainer(wizcard=wizcard,
                                     title=c.get('title', ""),
                                     company=c.get('company', ""),
                                     phone = c.get('phone', ""),
                                     start=c.get('start', ""),
                                     end=c.get('end', "Current"))
            t_row.save()

            if 'f_bizCardImage' in c and c['f_bizCardImage']:
                try:
                    rawimage = bytes(c['f_bizCardImage'])
                    #AA:TODO: better file name
                    upfile = SimpleUploadedFile("%s-f_bc.%s.%s.jpg" % \
                                                (wizcard.pk, t_row.pk, \
                                                 now().strftime("%Y-%m-%d %H:%M")), rawimage, \
                                                "image/jpeg")
                    t_row.f_bizCardImage.save(upfile.name, upfile)
                except:
                    pass
            elif 'f_bizCardUrl' in c:
                t_row.card_url = c['f_bizCardUrl']
                t_row.save()

        if flood:
            #AA:TODO: we also must notify the owner of the update
            notify.send(self.user, recipient=self.user,
                        verb=verbs.WIZWEB_WIZCARD_UPDATE[0],
                        target=wizcard)

            wizcard.flood()

        self.response.add_data("wizCardID", wizcard.id)
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
            uprofile = self.user.profile
            if uprofile.reco_ready != 0:
                uprofile.reco_ready = 0
                uprofile.save()
            genreco.send(self.user, recotarget=self.user.id)

        self.response.add_data("recos", recos)
        return self.response

    def SetRecoAction(self):
        recoid = self.sender['recoID'] if 'recoID' in self.sender else None
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

wizrequest_handler = WizRequestHandler.as_view()
#wizconnection_request = login_required(WizConnectionRequestView.as_view())
