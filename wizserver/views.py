""" .. autofunction:: wizconnection_request

.. autofunction:: wizconnection_accept

.. autofunction:: wizconnection_decline

.. autofunction:: wizconnection_cancel

.. autofunction:: wizconnection_delete

.. autofunction:: user_block

.. autofunction:: user_unblock
"""
import pdb
import json
import logging
from django.db.models import Q
from django.http import HttpResponse
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core import serializers
from lib.preserialize.serialize import serialize
from lib.ocr import OCR
from django.core.files.storage import default_storage
from django.contrib.contenttypes.models import ContentType
from wizcardship.models import WizConnectionRequest, Wizcard, ContactContainer, WizcardFlick
from notifications.models import notify, Notification
from virtual_table.models import VirtualTable
from response import Response, NotifResponse
from userprofile.models import UserProfile
from userprofile.models import FutureUser
from lib import wizlib
from wizcard import err
from location_mgr.models import LocationMgr
from dead_cards.models import DeadCards
from wizserver import msg_test, fields
from django.utils import timezone
import random
from django.core.cache import cache
from django.conf import settings
from lib.nexmomessage import NexmoMessage
import colander
from wizcard import message_format as message_format
from wizserver import verbs
from test import messages

now = timezone.now

logger = logging.getLogger(__name__)

class WizRequestHandler(View):
    def post(self, request, *args, **kwargs):
        self.request = request

        # Dispatch to appropriate message handler
        pdispatch = ParseMsgAndDispatch(self.request)
        response =  pdispatch.dispatch()
        logger.debug('sending response to app')
        #send response
        return response.respond()

class ParseMsgAndDispatch(object):
    def __init__(self, request):
        #validate header
        self.header = Header(request)

    def dispatch(self):
	status, response =  self.header.validate()
        if not status:
            return response

	return self.header.headerProcess()

    def dummy_validator(self, req):
        return req

    def securityException(self):
	#AA TODO
	return None
	
class Header(ParseMsgAndDispatch):
    def __init__(self, request):
        #raw message self.request = req
        #json deserialized
        self.request = request
        self.msg_type = None
	self.device_id = None
	self.password_hash = None
	self.user = None
	self.response = Response()
        self.msg = json.loads(request.body)

    def __repr__(self):
        if self.msg.has_key('header'):
            return str(self.msg['header'])

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


        return True

    def validateSender(self, sender):
	if not self.msg_is_initial():
	    try:
	        self.user = User.objects.get(id=sender['wizUserID'])
		self.userprofile = self.user.profile
	    except: 
                return False

	    if self.userprofile.userid != sender['userID']:
                return False
        
        #AA:TODO - Move to header
	if self.msg_has_location():
            self.lat = sender['lat']
            self.lng = sender['lng']
	        
        self.sender = sender

        return True

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
                            self.msgType)
            return False, self.response

	if self.msg.has_key('sender') and not self.validateSender(self.msg['sender']):
            self.securityException()
            self.response.ignore()
            logger.warning('user failed sender security check on msg {%s}', \
                            self.msgType)
            return False, self.response
        if 'receiver' in self.msg:
            self.receiver = self.msg['receiver']

        #AA:TODO: App to fix - This has to be in header
        self.on_wifi = self.sender['onWifi'] if \
                self.sender.has_key('onWifi') else False

        return True, self.response

    def headerProcess(self):

        msgTypesValidatorsAndHandlers = {
	    # wizweb messages
	    'wizweb_query_user'		  : (message_format.WizWebUserQuerySchema, self.WizWebUserQuery),
	    'wizweb_query_wizcard'	  : (message_format.WizWebWizcardQuerySchema, self.WizWebWizcardQuery),
	    'wizweb_create_user'	  : (message_format.WizWebUserCreateSchema, self.WizWebUserCreate),
	    'wizweb_add_edit_card'	  : (message_format.WizWebAddEditCardSchema, self.WizWebAddEditCard),
            'login'                       : (message_format.LoginSchema, self.Login),
            'phone_check_req'             : (message_format.PhoneCheckRequestSchema, self.PhoneCheckRequest),
            'phone_check_rsp'             : (message_format.PhoneCheckResponseSchema, self.PhoneCheckResponse),
            'register'                    : (message_format.RegisterSchema, self.Register),
            'current_location'            : (message_format.LocationUpdateSchema, self.LocationUpdate),
            'contacts_verify'	          : (message_format.ContactsVerifySchema, self.ContactsVerify),
            'get_cards'                   : (message_format.NotificationsGetSchema, self.NotificationsGet),
            'edit_card'                   : (message_format.WizcardEditSchema, self.WizcardEdit),
            'accept_connection_request'   : (message_format.WizcardAcceptSchema, self.WizcardAccept),
            'decline_connection_request'  : (message_format.WizConnectionRequestDeclineSchema, self.WizConnectionRequestDecline),
            #'delete_notification_card'    : (message_format.WizConnectionRequestDeclineSchema, self.WizConnectionRequestWithdraw),
            'withdraw_connection_request' : (message_format.WizConnectionRequestWithdrawSchema, self.WizConnectionRequestWithdraw),
            'delete_rolodex_card'         : (message_format.WizcardRolodexDeleteSchema, self.WizcardRolodexDelete),
            'card_flick'                  : (message_format.WizcardFlickSchema, self.WizcardFlick),
            'card_flick_accept'           : (message_format.WizcardFlickAcceptSchema, self.WizcardFlickAccept),
            'my_flicks'                   : (message_format.WizcardMyFlickSchema, self.WizcardMyFlicks),
            'flick_withdraw'              : (message_format.WizcardFlickWithdrawSchema, self.WizcardFlickWithdraw),
            'flick_edit'                  : (message_format.WizcardFlickEditSchema, self.WizcardFlickEdit),
            'query_flicks'                : (message_format.WizcardFlickQuerySchema, self.WizcardFlickQuery),
            'flick_pickers'               : (message_format.WizcardFlickPickersSchema, self.WizcardFlickPickers),
            'send_asset_to_xyz'           : (message_format.WizcardSendAssetToXYZSchema, self.WizcardSendAssetToXYZ),
            'send_card_to_contacts'       : (message_format.WizcardSendToContactsSchema, self.WizcardSendToContacts),
            'send_card_to_user'           : (message_format.WizcardSendUnTrustedSchema, self.WizcardSendUnTrusted),
            'send_card_to_future_user'    : (message_format.WizcardSendToFutureContactsSchema, self.WizcardSendToFutureContacts),
            'send_query_user'             : (message_format.UserQuerySchema, self.UserQuery),
            'get_card_details'            : (message_format.WizcardGetDetailSchema, self.WizcardGetDetail),
            'query_tables'                : (message_format.TableQuerySchema, self.TableQuery),
            'my_tables'                   : (message_format.TableMyTablesSchema, self.TableMyTables),
            'table_summary'               : (message_format.TableSummarySchema, self.TableSummary),
            'table_details'               : (message_format.TableDetailsSchema, self.TableDetails),
            'create_table'                : (message_format.TableCreateSchema, self.TableCreate),
            'join_table'                  : (message_format.TableJoinSchema, self.TableJoin),
            'leave_table'                 : (message_format.TableLeaveSchema, self.TableLeave),
            'destroy_table'               : (message_format.TableDestroySchema, self.TableDestroy),
            'table_edit'                  : (message_format.TableEditSchema, self.TableEdit),
            'settings'                    : (message_format.SettingsSchema, self.Settings),
            'ocr_req_self'                : (message_format.OcrRequestSelfSchema, self.OcrReqSelf),
            'ocr_req_dead_card'           : (message_format.OcrRequestDeadCardSchema, self.OcrReqDeadCard)
        }
        #update location since it may have changed
	if self.msg_has_location() and not self.msg_is_initial():
            self.userprofile.create_or_update_location(
			    self.lat,
			    self.lng)

        response = msgTypesValidatorsAndHandlers[self.msg_type][HANDLER]()

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
        test_mode = True if self.sender.has_key('test_mode') else False

        #AA_TODO: security check for checkMode type
	k_user = (settings.PHONE_CHECK_USER_KEY % username)
	k_device_id = (settings.PHONE_CHECK_DEVICE_ID_KEY % device_id)
	k_rand = (settings.PHONE_CHECK_USER_RAND_KEY % username)
	k_retry = (settings.PHONE_CHECK_USER_RETRY_KEY % username)

	user = cache.get(k_user)
	if user:
	    #should not be. Lets just clear it
	    cache.delete(k_user)

        d = dict()
	#new req, generate random num
	d[k_user] = username
	d[k_device_id] = device_id
	d[k_rand] = random.randint(settings.PHONE_CHECK_RAND_LOW, settings.PHONE_CHECK_RAND_HI)
	d[k_retry] = 1
	cache.set_many(d, timeout=settings.PHONE_CHECK_TIMEOUT)

        #send a text with the rand
        if settings.PHONE_CHECK:
            msg = settings.PHONE_CHECK_MESSAGE
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
                        d[k_rand]
            else:
                self.response.error_response(err.INVALID_MESSAGE)
                return self.response

            sms = NexmoMessage(msg)
            sms.set_text_info(msg['text'])
            sms.send_request()
            status, errStr = sms.get_response()

            if not status:
                #some error...let the app know
                self.response.error_response(err.NEXMO_SMS_SEND_FAILED)
                logger.error('nexmo send via (%s) failed to (%s) with err (%s)', response_mode, response_target, errStr)
                return self.response

        if test_mode:
            self.response.add_data("challenge_key", d[k_rand])

        return self.response

    def PhoneCheckResponse(self):
	username = self.sender['username']
	device_id = self.header['deviceID']
	challenge_response = self.sender['responseKey']

	if not (username and challenge_response):
            self.response.error_response(\
                    err.PHONE_CHECK_CHALLENGE_RESPONSE_DENIED)
            return self.response

	k_user = (settings.PHONE_CHECK_USER_KEY % username)
	k_rand = (settings.PHONE_CHECK_USER_RAND_KEY % username)
	k_retry = (settings.PHONE_CHECK_USER_RETRY_KEY % username)
	k_device_id = (settings.PHONE_CHECK_DEVICE_ID_KEY % device_id)

	d = cache.get_many([k_user, k_device_id, k_rand, k_retry], None)
        logger.info( "cached value for phone_check_xx {%s}", d)

        if d is None:
            self.response.error_response(err.PHONE_CHECK_TIMEOUT_EXCEEDED)
            return self.response

	if d[k_retry] > settings.MAX_PHONE_CHECK_RETRIES:
	    cache.delete(k_user)
            self.response.error_response(err.PHONE_CHECK_RETRY_EXCEEDED)
            logger.info('{%s} exceeded retry count', k_user)
            return self.response

        cache.incr(k_retry)

	if device_id != d[k_device_id]:
            logger.info('{%s} invalid device_id', k_user)
            self.response.error_response(err.PHONE_CHECK_CHALLENGE_RESPONSE_INVALID_DEVICE)
            return self.response

	if settings.PHONE_CHECK and challenge_response != d[k_rand]:
            logger.info('{%s} invalid challenge response', k_user)
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
	    # mark for sync.
	    user.profile.do_sync = True

	user.profile.device_id = device_id
	user.profile.save()

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
        try:
            self.userprofile.reg_token = self.sender['reg_token']
        except:
            pass

	if self.userprofile.do_sync:
            #sync all syncables
            s = self.userprofile.serialize_objects()
	    if 'wizcard' in s:
                self.response.add_data("wizcard", s['wizcard'])
		if 'wizconnections' in s:
                    self.response.add_data("rolodex", s['wizconnections'])
		if 'wizcard_flicks' in s:
                    self.response.add_data("wizcard_flicks", s['wizcard_flicks'])
	        if 'tables' in s:
                    self.response.add_data("tables", s['tables'])
                if 'flick_picks' in s:
                    self.response.add_data("flick_picks", s["flick_picks"])

                self.userprofile.activated = True

            self.userprofile.do_sync = False

	self.userprofile.save()

        return self.response

    def LocationUpdate(self):
        #update location in ptree
        self.userprofile.create_or_update_location(self.lat, self.lng)
        return self.response

    def ContactsVerify(self):
	verify_phone_list = self.receiver.get('verify_phones', [])
        verify_email_list = self.receiver.get('verify_emails', [])
        lp = []
        le = []

	count = 0
        for phone_number in verify_phone_list:
	    username = UserProfile.objects.username_from_phone_num(phone_number)
	    if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)

                if not user.profile.activated:
                    continue

		d = dict()
		d['phoneNum'] = phone_number
		d['wizUserID'] = user.id
		if Wizcard.objects.are_wizconnections(
				self.user.wizcard,
				user.wizcard):
		    d['tag'] = "connected"
		elif self.user == user:
		    d['tag'] = "own"
                else:
		    d['tag'] = "other"

		count += 1
	        lp.append(d)
        if count:
            self.response.add_data("count", count)
            self.response.add_data("verified_phones", lp)

	count = 0
        for email in verify_email_list:
            if Wizcard.objects.filter(email=email).exists():
                wizcard = Wizcard.objects.get(email=email)
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

		count += 1
	        le.append(d)
        if count:
            self.response.add_data("count", count)
            self.response.add_data("verified_emails", le)
            
        return self.response

    def NotificationsGet(self):
        notifications = Notification.objects.unread(self.user)
        notifResponse = NotifResponse(notifications)

        #i will be activated when I have a wizcard
        if not self.userprofile.activated:
            return self.response

	if self.lat == None and self.lng == None:
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
                self.lat, 
                self.lng, 
                settings.DEFAULT_MAX_LOOKUP_RESULTS)
        if count:
            notifResponse.notifFlickedWizcardsLookup(count, 
                    self.user, flicked_wizcards, 
		    self.userprofile.can_send_data(self.on_wifi))

        users, count = self.userprofile.lookup(settings.DEFAULT_MAX_LOOKUP_RESULTS)
        if count:
            notifResponse.notifUserLookup(count, self.user, users, 
			    self.userprofile.can_send_data(self.on_wifi))

        tables, count = VirtualTable.objects.lookup(
                self.lat, 
                self.lng, 
                settings.DEFAULT_MAX_LOOKUP_RESULTS)
        if count:
            notifResponse.notifTableLookup(count, self.user, tables)

        Notification.objects.mark_specific_as_read(notifications)

        #tickle the timer to keep it going and update the location if required 
        self.userprofile.create_or_update_location(self.lat, self.lng)
        return notifResponse

    def WizcardEdit(self):
        modify = False
        user_modify = False
        userprofile_modify = False

        try:
            wizcard = self.user.wizcard
        except ObjectDoesNotExist:
            wizcard = Wizcard(user=self.user)
            wizcard.save()

            #this is also the time User object can get first/last name
            self.userprofile.activated = True
            userprofile_modify = True

        #AA:TODO: Change app to call this phone as well
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

        if self.sender.has_key('thumbnailImage') and \
            self.sender['thumbnailImage']:
            rawimage = bytes(self.sender['thumbnailImage'])
            upfile = SimpleUploadedFile("%s-%s.jpg" % \
                    (wizcard.pk, now().strftime("%Y-%m-%d %H:%M")), 
                    rawimage, "image/jpeg")
            wizcard.thumbnailImage.save(upfile.name, upfile) 
            modify = True

	if 'contact_container' in self.sender:
            contactContainerList = self.sender['contact_container']
            wizcard.contact_container.all().delete()
            modify = True

            for count, contactItem in enumerate(contactContainerList):
	        if 'title' in contactItem:
                    title = contactItem['title']
                else:
                    title = ""
		if 'company' in contactItem:
                    company = contactItem['company']
                else:
                    company = ""
		if 'start' in contactItem:
                    start = contactItem['start']
                else:
                    start = ""
		if 'end' in contactItem:
                    end = contactItem['end']
                else:
                    end = ""

                #AA:TODO - Can there be 1 save with image
                c = ContactContainer(wizcard=wizcard,
				title=title,
				company=company,
				start=start,
				end=end)
		c.save()
		if 'f_bizCardImage' in contactItem and contactItem['f_bizCardImage']:
	            #AA:TODO: Remove try
                    try:
                        rawimage = bytes(contactItem['f_bizCardImage'])
			#AA:TODO: better file name
                        upfile = SimpleUploadedFile("%s-f_bc.%s.%s.jpg" % \
                                (wizcard.pk, c.pk, now().strftime\
                                ("%Y-%m-%d %H:%M")), rawimage, \
                                "image/jpeg")
                        c.f_bizCardImage.save(upfile.name, upfile) 
                    except:
                        pass
		if 'b_bizCardImage' in contactItem and contactItem['b_bizCardImage']:
	            #AA:TODO: Remove try
                    try:
                        rawimage = bytes(contactItem['b_bizCardImage'])
			#AA:TODO: better file name
                        upfile = SimpleUploadedFile("%s-b_bc.%s.%s.jpg" % (wizcard.pk, c.pk, now().strftime("%Y-%m-%d %H:%M")), rawimage, "image/jpeg")
                        c.b_bizCardImage.save(upfile.name, upfile) 
                    except:
                        pass

        #check if futureUser states exist for this phone or email
        future_users = FutureUser.objects.check_future_user(wizcard.email, phone)
        if future_users.count():
            for f in future_users:
                if ContentType.objects.get_for_model(f.content_object) == \
                        ContentType.objects.get(model="wizcard"):
                    Wizcard.objects.exchange(wizcard, f.content_object, False)
                elif ContentType.objects.get_for_model(f.content_object) == \
                        ContentType.objects.get(model="virtualtable"):
                    f.content_object.join_table_and_exchange(self.user,
                                                             None,
                                                             False,
                                                             True)

	    future_users.delete()
         
        #flood to contacts
        if user_modify:
            self.user.save()
        if userprofile_modify:
            self.userprofile.save()
        if modify:
            wizcard.save()
            wizcard.flood()

        self.response.add_data("wizCardID", wizcard.pk)

        return self.response

    def WizcardAccept(self):
        try:
            wizcard1 = self.user.wizcard
	    self.r_user = User.objects.get(id=self.receiver['wizUserID'])
            wizcard2 = self.r_user.wizcard
	except KeyError:
            self.securityException()
            self.response.ignore()
            return self.response
        except ObjectDoesNotExist:
	    self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        Wizcard.objects.accept_wizconnection(wizcard2, wizcard1)
        #Q this to the sender
        notify.send(self.user, recipient=self.r_user,
                    verb=verbs.WIZCARD_ACCEPT[0], 
                    target=wizcard1, 
                    action_object = wizcard2)

        return self.response

    def WizConnectionRequestDecline(self):
        try:
            wizcard1 = self.user.wizcard
            #AA: TODO Change to wizCardID
	    self.r_user = User.objects.get(id=self.receiver['wizUserID'])
            wizcard2 = self.r_user.wizcard
	except KeyError: 
            self.securityException()
            self.response.ignore()
            return self.response
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        #wizcard2 must have sent a wizconnection_request, lets clear it
        Wizcard.objects.wizconnection_req_clear(wizcard2, wizcard1)

        #AA:TODO: for now, this message also serves the reverse equation..ie, sender withdraws
        Wizcard.objects.wizconnection_req_clear(wizcard1, wizcard2)

        return self.response

    #AA: TODO: app needs to support this instead of above TODO
    #this is to withdraw sent request
    def WizConnectionRequestWithdraw(self):
        try:
            wizcard1 = self.user.wizcard
            #AA: TODO Change to wizCardID
            try:
	       wizcard2 = Wizcard.objects.get(id=self.receiver['wizCardID'])
               self.r_user = wizcard2.user
            except:
	       self.r_user = User.objects.get(id=self.receiver['wizUserID'])
               wizcard2 = self.r_user.wizcard
	except KeyError: 
            self.securityException()
            self.response.ignore()
            return self.response
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        #AA:TODO: Withdraw would only happen if the previously Q'd receiver 
        #notif is still unread. Remove it. if there is no notification, then
        # sender can't withdraw

        #also, the wizconnection request would have been unaccepted so far.
        #maybe can be used as a consistency check...

        #clear my wizconnection_request
        Wizcard.objects.wizconnection_req_clear(wizcard1, wizcard2)

        #send notif to the other guy to he can remove the corresponding 
        #request

        #on 2nd thoughts, this shouldn't be done since the new way is to
        #remove unread notification
        #notify.send(self.user, 
        #        recipient=self.r_user,
        #        verb=verbs.WIZCARD_WITHDRAW_REQUEST[0],
        #        target=wizcard1)

        return self.response
    def WizcardRolodexDelete(self):
	try:
            wizcard1 = self.user.wizcard
            wizcards = self.receiver['wizCardIDs']
            for w in wizcards:
                wizcard2 = Wizcard.objects.get(id=w)
                Wizcard.objects.uncard(wizcard1, wizcard2)
                #Q a notif to other guy so that the app on the other side can react
                notify.send(self.user, recipient=wizcard2.user, 
                        verb=verbs.WIZCARD_REVOKE[0],
                        target=wizcard1)
	except KeyError: 
            self.securityException()
            self.response.ignore()

        return self.response


    def WizcardFlick(self):
        try:
            wizcard = self.user.wizcard
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response
        timeout = self.sender['timeout']
        a_created = self.sender['created']

	if self.lat == None and self.lng == None:
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
	    t = flick_card.location.get().reset_timer()
            self.response.add_data("duplicate", True)
	    self.response.add_data("timeout", t.timeout_value/60)
        else:
	    flick_card = WizcardFlick.objects.create(wizcard=wizcard, 
                    lat=self.lat, 
                    lng=self.lng, 
                    timeout=timeout,
                    a_created = a_created)
            location = flick_card.create_location(self.lat, self.lng)
            location.start_timer(timeout)

        self.response.add_data("flickCardID", flick_card.pk)
        return self.response


    def WizcardFlickAccept(self):
	try:
            wizcard1 = self.user.wizcard
	except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response
        try:
            for flick_id in self.receiver['flickCardIDs']:
                flick_card = WizcardFlick.objects.get(id=flick_id)
                wizcard2 = flick_card.wizcard
	        #associate flick with user
	        flick_card.flick_pickers.add(wizcard1)
	        #create a wizconnection and then accept it
	        Wizcard.objects.exchange(wizcard1, wizcard2, True, \
                        flick_card=flick_card)
	except KeyError: 
            self.securityException()
            self.response.ignore()
            return self.response
	except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        return self.response

    def WizcardMyFlicks(self):
	self.wizcard = Wizcard.objects.get(id=self.sender['wizCardID'])
        my_flicked_cards = self.wizcard.flicked_cards.all()

	count = my_flicked_cards.count()
	if count:
	    flicks_s = WizcardFlick.objects.serialize(my_flicked_cards)
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
            timeout = self.sender['timeout']
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

        flicked_card.location.get().extend_timer(timeout)
        return self.response

    def WizcardFlickQuery(self):
        if not self.receiver.has_key('name'):
            self.securityException()
            self.response.ignore()
            return self.response

        result, count = WizcardFlick.objects.query_flicks(self.receiver['name'], None, None)

        if count:
            flicks_s = WizcardFlick.objects.serialize_split(self.user.wizcard, result, True, True)
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
                    template = fields.wizcard_template_brief_with_thumbnail)
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
        if receiver_type in ['wiz_untrusted', 'wiz_trusted']:
            if receiver_type == 'wiz_trusted':
                implicit = True
            else:
                implicit = False
            #receiverIDs has wizUserIDs
            for id in receivers:
                r_user = User.objects.get(id=id)
                r_wizcard = r_user.wizcard

                if not Wizcard.objects.are_wizconnections(wizcard, r_wizcard):
                    Wizcard.objects.exchange(wizcard, r_wizcard, implicit)
                    count += 1
                self.response.add_data("count", count)
        elif receiver_type in ['email', 'sms']:
            #future user handling
            self.do_future_user(wizcard, receiver_type, receivers)

        return self.response

    def WizcardSendTableToXYZ(self, table, receiver_type, receivers):
        if receiver_type in ['wiz_untrusted', 'wiz_trusted']:
            #receiverIDs has wizUserIDs
            for id in receivers:
                r_user = User.objects.get(id=id)
                notify.send(self.user, recipient=r_user,
                    verb=verbs.WIZCARD_TABLE_INVITE[0], 
                    target=table, 
                    action_object = self.user)
        elif receiver_type in ['email', 'sms']:
            #create future user
            self.do_future_user(table, receiver_type, receivers)

        return self.response

    def do_future_user(self, obj, receiver_type, receivers):
        if receiver_type == 'sms':
            for phone in receivers:
                FutureUser(
                    content_type=ContentType.objects.get_for_model(obj),
                    object_id=obj.id,
                    phone=phone).save()
        else:
            for email in receivers:
                FutureUser(
                    content_type=ContentType.objects.get_for_model(obj),
                    object_id=obj.id,
                    email=email).save()

    def WizcardSendToContacts(self):
        #implicitly create a bidir cardship (since this is from contacts)
        #and also Q the other guys cards here
        count = 0
        try:
            wizcard1 = self.user.wizcard
        except ObjectDoesNotExist:
	    self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        phones = self.receiver['phones']
        for phone in phones:
            try:
                #AA:TODO: phone should just be the mobile phone. App needs to change
                # to adjust this. Also, array is not required
                #cphone = wizlib.convert_phone(phone)
                username = UserProfile.objects.username_from_phone_num(phone)
                try:
                    r_user = UserProfile.objects.get(username=username)
                    wizcard2 = r_user.wizcard
                except:
                    continue
                if not Wizcard.objects.are_wizconnections(wizcard1, wizcard2):
	            Wizcard.objects.exchange(wizcard1, wizcard2, True)
		    count += 1

            except:
	        self.response.error_response(err.INTERNAL_ERROR)

        self.response.add_data("count", count)
        return self.response


    def WizcardSendUnTrusted(self):
        try:
            wizcard1 = self.user.wizcard
            self.receivers = self.receiver['wizUserIDs']
	except KeyError: 
            self.securityException()
            self.response.ignore()
            return self.response
        except ObjectDoesNotExist:
	    self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        for receiver in self.receivers:
            try:
                wizcard2 = User.objects.get(id=receiver).wizcard
                ret = Wizcard.objects.exchange(wizcard1, wizcard2, False)
                if ret['errno']:
                    self.response.error_response(ret)
            except:
                self.response.error_response(err.INTERNAL_ERROR)

        return self.response


    def WizcardSendToFutureContacts(self):
        wizcard1 = self.user.wizcard
        for phone in self.receiver['phones']:
            username = UserProfile.objects.futureusername_from_phone_num(
			    wizlib.convert_phone(phone)
			    )
            #create a dummy user using the phone number as userID
            try:
                r_user, created = User.objects.get_or_create(username=username)
                if created:
                    wizcard2 = Wizcard(user=r_user).save()
                    r_user.profile.set_future()
		else:
		    #must have been previously future created
		    wizcard2 = r_user.wizcard

                err = Wizcard.objects.exchange(wizcard1, wizcard2, False)
		if err['errno']:
                    self.response.error_response(err)
            except:
                pass
        return self.response

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

        if (count):
            users_s = Wizcard.objects.serialize(result, 
                    template=fields.wizcard_template_brief_with_thumbnail)
            self.response.add_data("queryResult", users_s)
        self.response.add_data("count", count)
 
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
	tables = self.user.tables.all()
	count = tables.count()
	if count:
	    tables_s = VirtualTable.objects.serialize(tables)
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
            out = UserProfile.objects.serialize_split(self.user, 
                    members,
		    self.userprofile.can_send_data(self.on_wifi))
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
        send_data = self.userprofile.can_send_data(self.on_wifi)

        if r_userprofile.is_profile_private:
            if send_data:
                template = fields.wizcard_template_brief_with_thumbnail
            else:
                template = fields.wizcard_template_brief
        else:
            if send_data:
                template = fields.wizcard_template_full
            else:
                template = fields.wizcard_template_extended

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
        
        #TODO: AA handle create failure and/or unique name enforcement
        #update location in ptree
        #AA:TODO move create to overridden create in VirtualTable
        table.create_location(self.lat, self.lng)
        l = table.location.get()
	l.start_timer(timeout)
        #AA:TODO why do we need this ?
        table.join_table_and_exchange(self.user, password, False)
        table.save()
        self.response.add_data("tableID", table.pk)
        return self.response


    def TableJoin(self):
        try:
            table = VirtualTable.objects.get(id=self.sender['tableID'])
        except ObjectDoesNotExist:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        if self.user is table.creator:
            self.response.error_response(err.EXISTING_MEMBER)
            return self.response

        if table.is_secure():
            password = self.sender['password']
        else:
            password = None
        
        joined = table.join_table_and_exchange(self.user, password, True)

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
            a_created = self.sender['created']
            table.a_created = a_created
            table.location.get().extend_timer(self.sender['timeout'])
        table.save()

        self.response.add_data("tableID", table.pk)
	return self.response

    def Settings(self):
	modify = False

        if self.sender.has_key('media'):
            if self.sender['media'].has_key('wifiOnly'):
                wifi_data = self.sender['media']['wifiOnly']
                if self.userprofile.is_wifi_data != wifi_data:
                    self.userprofile.is_wifi_data = wifi_data
                    modify = True
        
	if self.sender.has_key('privacy'):
	    if self.sender['privacy'].has_key('invisible'):
		visible_nearby = not(self.sender['privacy']['invisible'])
		if self.userprofile.is_visible_nearby != visible_nearby:
		    self.userprofile.is_visible_nearby = visible_nearby
                    modify = True

	    if self.sender['privacy'].has_key('blockUnsolicited'):
		block_unsolicited = not(self.sender['privacy']['blockUnsolicited'])
		if self.userprofile.block_unsolicited != block_unsolicited:
		    self.userprofile.block_unsolicited = block_unsolicited
		    modify = True

	    if self.sender['privacy'].has_key('publicTimeline'):
		profile_private = not(self.sender['privacy']['publicTimeline'])
		if self.userprofile.is_profile_private != profile_private:
		    self.userprofile.is_profile_private = profile_private
		    modify = True

        if modify == True:
	    self.userprofile.save()
	  
	return self.response

    #############OCR MessageS##############
    def OcrReqSelf(self):
        try:
            wizcard = self.user.wizcard
        except ObjectDoesNotExist:
            #this is the expected case
            wizcard = Wizcard(user=self.user)
            wizcard.save()

        c = ContactContainer(wizcard=wizcard)
        c.save()

        if self.sender.has_key('f_ocrCardImage'): 
            rawimage = bytes(self.sender['f_ocrCardImage'])
            #AA:TODO maybe time to put this in lib
            upfile = SimpleUploadedFile("%s-%s.jpg" % \
                    (wizcard.pk, now().strftime("%Y-%m-%d %H:%M")),
                    rawimage, "image/jpeg") 
            
            c.f_bizCardImage.save(upfile.name, upfile)
            path = c.f_bizCardImage.local_path()
        else:
            #AA. TODO: Remove me eventually...this is just for testing
            path = "test/photo.JPG"

        #Do ocr stuff
        ocr = OCR()
        result = ocr.process(path)
        #AA:TODO Error handling

        wizcard.first_name = result.get('first_name', "")
        wizcard.last_name = result.get('last_name', "")
        wizcard.phone = result.get('phone', "")
        wizcard.email = result.get('email', "")
        wizcard.save()

        c.title = result.get('title', ""),
        c.company = result.get('company', "")
        c.end="current"
        c.save()

        self.response.add_data("ocr_result", result)
        print "sending OCR scan results", result
        return self.response

    def OcrReqDeadCard(self):
        try:
            wizcard = self.user.wizcard
        except ObjectDoesNotExist:
	    self.response.error_response(err.CRITICAL_ERROR)
            return self.response

        d = DeadCards(user=self.user)
        d.save()

        if self.sender.has_key('f_ocrCardImage'): 
            rawimage = bytes(self.sender['f_ocrCardImage'])
            #AA:TODO maybe time to put this in lib
            
            d.f_bizCardImage.save(upfile.name, upfile)
            path = d.f_bizCardImage.local_path()
        else:
            path = "test/photo.JPG"
            rawimage = bytes(open(path).read())
            #AA:TODO Remove me eventually...this is just for testing

        upfile = SimpleUploadedFile("%s-%s.jpg" % \
                (wizcard.pk, now().strftime("%Y-%m-%d %H:%M")),
                rawimage, "image/jpeg")
        d.f_bizCardImage.save(upfile.name, upfile)

        d.recognize()
        self.response.add_data("response", d.serialize())
        return self.response

    #################WizWeb Message handling########################
    def WizWebUserQuery(self):
	username = self.sender['username']
	userID = None
	try:
	    user = User.objects.get(username=username)
            self.response.add_data("userID", user.profile.userid)
	except:
	    pass
        
	return self.response

    def WizWebWizcardQuery(self):
	username = self.sender['username']
	userID = self.sender['userID']

        try:
	    self.user = User.objects.get(username=username)
	except:
            return self.response.error_response(err.USER_DOESNT_EXIST)

        if self.user.profile.userid != userID:
            return self.response.error_response(err.VALIDITY_CHECK_FAILED)

	try:
            wizcard = self.user.wizcard
	except:
            return self.response.error_response(err.VALIDITY_CHECK_FAILED)

        out = wizcard.serialize()
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
            future_users = FutureUser.objects.check_future_user(wizcard.email, phone)
            if future_users.count():
                for f in future_users:
                    if ContentType.objects.get_for_model(f.content_object) == \
                            ContentType.objects.get(model="wizcard"):
                                Wizcard.objects.exchange(wizcard, f.content_object, False)
                    elif ContentType.objects.get_for_model(f.content_object) == \
                            ContentType.objects.get(model="virtualtable"):
                                f.content_object.join_table_and_exchange(self.user,
                                        None,
                                        False,
                                        True)

	    future_users.delete()

        for c in contact_container:
            title = "FIXME" if not c['title'] else c['title']
	    t_row = ContactContainer(wizcard=wizcard,
                    title=title,
                    #title=c['title'],
                    company=c['company'],
                    start=c['start'],
                    end=c['end'])
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

	if flood == True:
            #AA:TODO: we also must notify the owner of the update
            notify.send(self.user, recipient=self.user,
                    verb=verbs.WIZWEB_WIZCARD_UPDATE[0], 
                    target=wizcard, 
                    action_object = wizcard)

	    wizcard.flood()

        self.response.add_data("wizCardID", wizcard.id)
	return self.response
	    

VALIDATOR = 0
HANDLER = 1



wizrequest_handler = WizRequestHandler.as_view()
#wizconnection_request = login_required(WizConnectionRequestView.as_view())
