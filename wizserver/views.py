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
from django.core.files.storage import default_storage
from wizcardship.models import WizConnectionRequest, Wizcard, ContactContainer, WizcardFlick
from notifications.models import notify, Notification
from virtual_table.models import VirtualTable
from response import Response, NotifResponse
from userprofile.models import UserProfile
from lib import wizlib
from wizcard import err
from location_mgr.models import LocationMgr
import msg_test, fields
from django.utils import timezone
import random
from django.core.cache import cache
from django.conf import settings
from nexmomessage import NexmoMessage
import colander
from wizcard import message_format as message_format

now = timezone.now

#logger = logging.getLogger(__name__)

class WizRequestHandler(View):
    def post(self, request, *args, **kwargs):
        self.request = request

        # Dispatch to appropriate message handler
        pdispatch = ParseMsgAndDispatch(self.request)
        response =  pdispatch.dispatch()
        print 'sending response to app', response
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
	print 'ALERT ALERT!! FIXME'
	return None
	
class Header(ParseMsgAndDispatch):
    def __init__(self, request):
        #raw message self.request = req
        #json deserialized
        self.request = request
        self.msg = json.loads(request.body)
        self.msg_type = None
	self.device_id = None
	self.password_hash = None
	self.user = None
	self.response = Response()

    def __repr__(self):
        return str(self.msg)

    def msg_has_location(self):
        return ('lat' in self.msg['header'] and 'lng' in self.msg['header']) or ('lat' in self.msg['sender'] and 'lng' in self.msg['sender'])

    def msg_is_initial(self):
	return self.msg_type in ['phone_check_req', 'phone_check_rsp', 'login'] 

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

    def validate(self):
        try:
            #self.header = message_format.CommonHeaderSchema().deserialize(self.msg['header'])
            self.header = self.msg['header']
        except colander.Invalid:
            self.response.ignore()
            return False

	self.msg_type = self.header['msgType']
        print 'received message', self.msg_type
        print self

	if not self.validateHeader():
            self.securityException()
            self.response.ignore()
            return False, self.response

	if 'sender' in self.msg and not self.validateSender(self.msg['sender']):
            self.securityException()
            self.response.ignore()
            return False, self.response
        if 'receiver' in self.msg:
            self.receiver = self.msg['receiver']

        return True, self.response

    def headerProcess(self):

        msgTypesValidatorsAndHandlers = {
            'login'                       : (message_format.LoginSchema, self.Login),
            'phone_check_req'             : (message_format.PhoneCheckRequestSchema, self.PhoneCheckRequest),
            'phone_check_rsp'             : (message_format.PhoneCheckResponseSchema, self.PhoneCheckResponse),
            'register'                    : (message_format.RegisterSchema, self.Register),
            'current_location'            : (message_format.LocationUpdateSchema, self. LocationUpdate),
            'contacts_verify'	          : (message_format.ContactsVerifySchema, self. ContactsVerify),
            'get_cards'                   : (message_format.NotificationsGetSchema, self. NotificationsGet),
            'edit_card'                   : (message_format.WizcardEditSchema, self. WizcardEdit),
            'add_notification_card'       : (message_format.WizcardAcceptSchema, self. WizcardAccept),
            'delete_notification_card'    : (message_format.WizConnectionRequestDeclineSchema, self.WizConnectionRequestDecline),
            'delete_rolodex_card'         : (message_format.WizcardRolodexDeleteSchema, self.WizcardRolodexDelete),
            'card_flick'                  : (message_format.WizcardFlickSchema, self.WizcardFlick),
            'card_flick_accept'           : (message_format.WizcardFlickAcceptSchema, self.WizcardFlickAccept),
            'my_flicks'                   : (message_format.WizcardMyFlickSchema, self.WizcardMyFlicks),
            'flick_withdraw'              : (message_format.WizcardFlickWithdrawSchema, self.WizcardFlickWithdraw),
            'flick_extend'                : (message_format.WizcardFlickExtendSchema, self.WizcardFlickExtend),
            'send_card_to_contacts'       : (message_format.WizcardSendToContactsSchema, self.WizcardSendToContacts),
            'send_card_to_user'           : (message_format.WizcardSendUnTrustedSchema, self.WizcardSendUnTrusted),
            'send_card_to_future_contacts': (message_format.WizcardSendToFutureContactsSchema, self.WizcardSendToFutureContacts),
            'find_users_by_location'      : (message_format.UserQueryByLocationSchema, self.UserQueryByLocation),
            'send_query_user'             : (message_format.UserQueryByNameSchema, self.UserQueryByName),
            'show_user_details'           : (message_format.UserGetDetailSchema, self.UserGetDetail),
            'show_table_list'             : (message_format.TableQuerySchema, self.TableQuery),
            'my_tables'                   : (message_format.TableMyTablesSchema, self.TableMyTables),
            'table_details'               : (message_format.TableDetailsSchema, self.TableDetails),
            'create_table'                : (message_format.TableCreateSchema, self.TableCreate),
            'join_table'                  : (message_format.TableJoinSchema, self.TableJoin),
            'leave_table'                 : (message_format.TableLeaveSchema, self.TableLeave),
            'destroy_table'               : (message_format.TableDestroySchema, self.TableDestroy),
            'rename_table'                : (message_format.TableRenameSchema, self.TableRename)
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
        if not self.msg_is_initial():
	    cache.set('seen_%s' % (self.user), now(), 
		    settings.USER_LASTSEEN_TIMEOUT)

    def PhoneCheckRequest(self):
	device_id = self.header['deviceID']
	username = self.sender['username']
	response_mode = self.sender['responseMode']
	response_target = self.sender['target']

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

	if response_mode == "voice":
	    #TODO
	    pass

        #send a text with the rand
        if settings.PHONE_CHECK:
            msg = settings.PHONE_CHECK_MESSAGE
            msg['to'] = response_target
            msg['text'] = settings.PHONE_CHECK_RESPONSE_GREETING % d[k_rand]
            sms = NexmoMessage(msg)
            sms.set_text_info(msg['text'])
            response = sms.send_request()
            if response['messages'][0]['status'] != '0':
                #some error...let the app know
                return self.response.error_response(err.NEXMO_SMS_SEND_FAILED)

        return self.response

    def PhoneCheckResponse(self):
	username = self.sender['username']
	device_id = self.header['deviceID']
	challenge_response = self.sender['responseKey']

	if not (username and challenge_response):
            return self.response.error_response(err.PHONE_CHECK_CHALLENGE_RESPONSE_DENIED)

	k_user = (settings.PHONE_CHECK_USER_KEY % username)
	k_rand = (settings.PHONE_CHECK_USER_RAND_KEY % username)
	k_retry = (settings.PHONE_CHECK_USER_RETRY_KEY % username)
	k_device_id = (settings.PHONE_CHECK_DEVICE_ID_KEY % device_id)

	d = cache.get_many([k_user, k_device_id, k_rand, k_retry])

	#AA:TODO: put this in try, except...for invalid usernames

	if d[k_retry] > settings.MAX_PHONE_CHECK_RETRIES:
	    cache.delete(k_user)
            return self.response.error_response(err.PHONE_CHECK_RETRY_EXCEEDED)

        cache.incr(k_retry)

	if device_id != d[k_device_id]:
            return self.response.error_response(err.PHONE_CHECK_CHALLENGE_RESPONSE_INVALID_DEVICE)

	if settings.PHONE_CHECK and challenge_response != d[k_rand]:
            return self.response.error_response(err.PHONE_CHECK_CHALLENGE_RESPONSE_DENIED)

        #response is valid. create user here and send back userID
	user, created = User.objects.get_or_create(username=username)

	if created:
	    #AA TODO: Generate hash from deviceID and user.pk
	    password = "wizcard"
	    #password = user.profile.gen_password(user.pk, device_id)
	    user.set_password(password)
	    #generate internal userid
	    user.save()
	    user.profile.userid = UserProfile.objects.id_generator()
	else:
	    # mark for sync.
	    user.profile.do_sync = True

	user.profile.device_id = device_id
	user.profile.save()

	#AA TODO: Maybe not here, but making a note. profile is created as
	# soon as user is created...so, searching for users should filter on 
	#is_active on some such flag

	
	#all done. #clear cache
	cache.delete_many([k_user, k_device_id, k_rand, k_retry])

	user.profile.save()

        self.response.add_data("userID", user.profile.userid)
        return self.response

    def Login(self):
	self.username = self.sender['username']
        self.user = User.objects.get(username=self.username)
	self.password = "wizcard"
        auth = authenticate(username=self.username, password=self.password)
        if auth is None:
            #invalid password
            self.response.error_response(err.AUTHENTICATION_FAILED)
            return self.response

        self.response.add_data("wizUserID", self.user.pk)
        return self.response

    def Register(self):
        print '{sender} at location [{locX} , {locY}] sent '.format (sender=self.sender['userID'], locX=self.sender['lat'], locY=self.sender['lng'])

        #sync the app from server

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
                self.response.add_data("wizcards", s['wizcard'])
		if 'wizconnections' in s:
                    self.response.add_data("rolodex", s['wizconnections'])
		if 'wizcard_flicks' in s:
                    self.response.add_data("wizcard_flicks", s['wizcard_flicks'])
	        if 'tables' in s:
                    self.response.add_data("tables", s['tables'])
                if 'flick_picks' in s:
                    self.response.add_data("flick_picks", s["flick_picks"])

            self.userprofile.sync = False

	self.userprofile.save()

        #update location in ptree
	if self.lat != None and self.lng != None:
            self.userprofile.create_or_update_location(self.lat, self.lng)

        return self.response

    def LocationUpdate(self):
        #update location in ptree
        self.userprofile.create_or_update_location(self.lat, self.lng)
        return self.response

    def ContactsVerify(self):
	verify_list = self.receiver['verify_list']
	l = list()
	count = 0

        for phone_number in verify_list:
	    username = (phone_number + settings.WIZCARD_USERNAME_EXTENSION)
	    if User.objects.filter(username=username).exists():
		count += 1
	        l.append(phone_number)

        self.response.add_data("count", count)
        self.response.add_data("phoneNumberVerify", l)
        return self.response

    def NotificationsGet(self):
        notifications = Notification.objects.unread(self.user)
        notifResponse = NotifResponse(notifications)

        if not Wizcard.objects.filter(user=self.user).exists():
            return self.response


	if self.lat == None and self.lng == None:
	    try:
	        self.lat = self.userprofile.location.get().lat
		self.lng = self.userprofile.location.get().lng
	    except:
                #maybe location timedout. Shouldn't happen if messages from app
                #are coming correctly...
                print ' No location information available'
		return self.response
	    

        #any wizcards dropped nearby
        #AA:TODO: Use come caching framework to cache these
        flicked_wizcards, count = WizcardFlick.objects.lookup(
                self.lat, 
                self.lng, 
                settings.DEFAULT_MAX_LOOKUP_RESULTS)
        if count:
	    #AA_TODO: ios app crashes if thumbnail is included. This should be
	    #natively done when app is fixed (also for tables and users)
            notifResponse.notifFlickedWizcardsLookup(count, 
                    self.user, flicked_wizcards, True)

        users, count = self.userprofile.lookup(settings.DEFAULT_MAX_LOOKUP_RESULTS)
        if count:
            notifResponse.notifUserLookup(count, users, True)

        #tables is a smaller entity...get the tables as well instead of just count
        tables, count = VirtualTable.objects.lookup(
                self.lat, 
                self.lng, 
                settings.DEFAULT_MAX_LOOKUP_RESULTS)
        if count:
            notifResponse.notifTableLookup(count, self.user, tables)

        Notification.objects.mark_all_as_read(self.user)

        #tickle the timer to keep it going and update the location if required 
        self.userprofile.create_or_update_location(self.lat, self.lng)
        return notifResponse

    def WizcardEdit(self):
        modify = False
        try:
            wizcard = self.user.wizcard
        except ObjectDoesNotExist:
            #create case
            wizcard = Wizcard(user=self.user)
            wizcard.save()

            #this is also the time User object can get first/last name
            self.user.first_name = self.sender['first_name']
            self.user.last_name = self.sender['last_name']
            self.user.save()

        phone1 = self.sender['phone1']

        #check if futureUser existed for this phoneNum
        try:
            future_user = User.objects.get(username=phone1)
            if future_user.profile.is_future():
                Wizcard.objects.migrate_future_user(future_user, self.user)
                Notification.objects.migrate_future_user(future_user, self.user)
            future_user.delete()
        except:
            pass

        if wizcard.phone1 != phone1:
            wizcard.phone1 = phone1
            modify = True

	if 'first_name' in self.sender:
            first_name = self.sender['first_name']
            if wizcard.first_name != first_name:
                wizcard.first_name = first_name
                modify = True
	if 'last_name' in self.sender:
            last_name = self.sender['last_name']
            if wizcard.last_name != last_name:
                wizcard.last_name = last_name
                modify = True
	if 'phone2' in self.sender:
            phone2 = self.sender['phone2']
            if wizcard.phone2 != phone2:
                wizcard.phone2 = phone2
                modify = True
	if 'email' in self.sender:
            email = self.sender['email']
            if wizcard.email != email:
                wizcard.email = email
                modify = True
	if 'address_street1' in self.sender:
            street1 = self.sender['address_street1']
            if wizcard.address_street1 != street1:
                wizcard.address_street1 = street1
                modify = True
	if 'address_city' in self.sender:
            city = self.sender['address_city']
            if wizcard.address_city != city:
                wizcard.address_city = city
                modify = True
	if 'address_state' in self.sender:
            state = self.sender['address_state']
            if wizcard.address_state != state:
                wizcard.address_state = state
                modify = True
	if 'address_country' in self.sender:
            country = self.sender['address_country']
            if wizcard.address_country != country:
                wizcard.address_country = country
                modify = True
	if 'address_zip' in self.sender:
            zipcode = self.sender['address_zip']
            if wizcard.address_zip != zipcode:
                wizcard.address_zip = zipcode
                modify = True

        if 'thumbnailImage' in self.sender:
        #if 'thumbnailImage' in self.sender and self.sender['imageWasEdited']:
	    #AA:TODO: Remove try
            try:
                rawimage = bytes(self.sender['thumbnailImage'])
                upfile = SimpleUploadedFile("%s-%s.jpg" % (wizcard.pk, now().strftime("%Y-%m-%d %H:%M")), rawimage, "image/jpeg")
                wizcard.thumbnailImage.save(upfile.name, upfile) 
                modify = True
            except:
                pass

	if 'videoUrl' in self.sender:
            rawvideo = self.sender['VideoUrl']
            upfile = SimpleUploadedFile("%s-%s.mp4" % (wizcard.pk, now().strftime("%Y-%m-%d %H:%M")), rawvideo, "video/mp4")
            wizcard.video.save(upfile.name, upfile) 
            modify = True

	if 'contactContainer' in self.sender:
            contactContainerList = self.sender['contactContainer']
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

                #AA:TODO - Can there be 1 save with image
                c = ContactContainer(wizcard=wizcard, title=title, company=company)
		c.save()
		if 'f_bizCardImage' in contactItem and contactItem['f_bizCardImage']:
	            #AA:TODO: Remove try
                    try:
                        rawimage = bytes(contactItem['f_bizCardImage'])
			#AA:TODO: better file name
                        upfile = SimpleUploadedFile("%s-f_bc.%s.%s.jpg" % (wizcard.pk, c.pk, now().strftime("%Y-%m-%d %H:%M")), rawimage, "image/jpeg")
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

        #flood to contacts
        if modify:
            wizcard.save()
            wizcard.flood()

        self.response.add_data("wizCardID", wizcard.pk)

        return self.response

    def WizcardAccept(self):
	self.r_user = User.objects.get(id=self.receiver['wizUserID'])
        try:
            wizcard1 = self.user.wizcard
            wizcard2 = self.r_user.wizcard
        except ObjectDoesNotExist:
	    self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        Wizcard.objects.accept_wizconnection(wizcard2, wizcard1)
        #Q this to the sender 
        notify.send(self.user, recipient=self.r_user,
                    verb='accepted wizcard', target=wizcard1, 
                    action_object = wizcard2)

        return self.response

    def WizConnectionRequestDecline(self):
        try:
            wizcard1 = self.user.wizcard
            wizcard2 = self.r_user.wizcard
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        #wizcard2 must have sent a wizconnection_request, lets clear it
        Wizcard.objects.wizconnection_req_clear(wizcard2, wizcard1)

        #Q a notif to other guy so that the app on the other side can react
	#AA:TODO: Should we send this at all ?? better for the other 
	#guy to not know
        notify.send(self.user, recipient=self.r_user,
                    verb='revoked wizcard', target=wizcard1)

        return self.response


    def WizcardRolodexDelete(self):
	try:
	    self.r_user = User.objects.get(id=self.receiver['wizUserID'])
	except: 
	    try:
	        self.r_user = UserProfile.objects.get(id=self.receiver['userID']).user
	    except:
                self.response.error_response(err.USER_DOESNT_EXIST)
	        return self.response
        try:
            wizcard1 = self.user.wizcard
            wizcard2 = self.r_user.wizcard
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        Wizcard.objects.uncard(wizcard1, wizcard2)
        #Q a notif to other guy so that the app on the other side can react
        notify.send(self.user, recipient=self.r_user,
                    verb='revoked wizcard', target=wizcard1)
        return self.response


    def WizcardFlick(self):
        try:
            wizcard = self.user.wizcard
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response
        try:
            flick_timeout = self.sender['flickTimeout']
        except:
            flick_timeout = settings.WIZCARD_FLICK_DEFAULT_TIMEOUT

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
	    flick_card.location.get().reset_timer()
        else:
	    flick_card = WizcardFlick.objects.create(wizcard=wizcard, lat=self.lat, lng=self.lng)
            location = flick_card.create_location(self.lat, self.lng)
            location.start_timer(flick_timeout)

        self.response.add_data("flickCardID", flick_card.pk)
        return self.response


    def WizcardFlickAccept(self):
	try:
            wizcard1 = self.user.wizcard
            wizcard2 = Wizcard.objects.get(id=self.receiver['wizcardID'])
	except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response
        try:
            flick_card = WizcardFlick.objects.get(id=self.receiver['flickCardID'])
	except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

	#create a wizconnection and then accept it
	Wizcard.objects.exchange(wizcard1, wizcard2, True)

	#associate flick with user
	flick_card.flick_pickers.add(self.user)

	#q notif to owner of flicked card 
        notify.send(wizcard1.user, recipient=wizcard2.user,
                    verb='flick pick', target=wizcard2, 
                    action_object = flick_card)

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
	except: 
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
	    return self.response

	self.flicked_card.delete()
	return self.response


    def WizcardFlickExtend(self):
	try:
	    self.flicked_card = WizcardFlick.objects.get(id=self.sender['flickCardID'])
	except: 
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
	    return self.response

	location = self.flicked_card.location
	location.extend_timer(self.timeout)
        return self.response


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
                cphone = wizlib.convert_phone(phone)
                target_wizcards, query_count = Wizcard.objects.find_users(
				sender.pk, 
				None, 
				cphone, 
				None)
		if query_count:
		    for wizcard2 in target_wizcards:
		        #create bidir cardship
                        if not Wizcard.objects.are_wizconnections(wizcard1, wizcard2):
			    err = Wizcard.objects.exchange(wizcard1, wizcard2, True)
			    count += 1
                    else:
                        #future contacts
                        return self.processSendCardToFutureContacts(phones, sender)

            except:
	        self.response.error_response(err.INTERNAL_ERROR)

        self.response.add_data("count", count)
        return self.response


    def WizcardSendUnTrusted(self):
        self.receivers = self.des['receiver']['wizUserIDs']
        try:
            wizcard1 = self.user.wizcard
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
        for phone in self.receiver['phones']:
            username = wizlib.convert_phone(phone)
            #create a dummy user using the phone number as userID
            try:
                #TODO: handle multiple phones or restrict app to send one
                receiver, created = User.objects.get_or_create(username=username)
                if created:
                    Wizcard(user=receiver).save()
                    receiver.profile.set_future()
                else:
                    assert receiver.profile.is_future(), 'not a future user'

                err = Wizcard.objects.exchange(wizcard, receiver.wizcard, False)
		if err['errno']:
                    self.response.error_response(err)
            except:
                pass
        return self.response


    def UserQueryByLocation(self):
        #update location in ptree
        self.userprofile.create_or_update_location(self.sender['lat'], 
                                          self.sender['lng'])
        lookup_result, count = self.userprofile.lookup(settings.DEFAULT_MAX_LOOKUP_RESULTS)
        if count:
            users_s = UserProfile.objects.serialize(lookup_result)
            self.response.add_data("queryResult", users_s)
        self.response.add_data("count", count)

        return self.response


    def UserQueryByName(self):
        self.receiver = self.des['receiver']
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

        lookup_result, count = Wizcard.objects.find_users(self.user, name, phone, email)
        #send back to app for selection

        if (count):
            users = UserProfile.objects.serialize(lookup_result)
            self.response.add_data("queryResult", users)
        self.response.add_data("count", count)
 
        return self.response


    def TableQuery(self):
        if self.sender.has_key('lat') and self.sender.has_key('lng'):
            lat = self.sender['lat']
            lng = self.sender['lng']
            self.QueryTableByLocation(lat, lng)
        elif self.sender.has_key('table_name'):
            name = self.sender['table_name']
            self.QueryTableByName(name)
        else:
            return self.securityException()

        return self.response

    def QueryTableByName(self, name):
        try:
            tables = VirtualTable.objects.filter(Q(tablename__icontains=name))
        except ObjectDoesNotExist:
            self.response.error_response(err.NONE_FOUND)
            return self.response
        count = tables.count()

        if count:
	    tables_s = VirtualTable.objects.serialize(tables)
            self.response.add_data("queryResult", tables_s)
        self.response.add_data("count", count)
            
        return self.response

    def QueryTableByLocation(self, lat, lng):
        tables, count = VirtualTable.objects.lookup(
                lat=lat, 
                lng=lng, 
                n=settings.DEFAULT_MAX_LOOKUP_RESULTS)
        if count:
            tables_s = VirtualTable.objects.serialize(tables)
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


    def TableDetails(self):
        #get the members
        table = VirtualTable.objects.get(id=self.sender['tableID'])
        memberships = table.membership_set.all()
        count = memberships.count()
        if count:
            members = map(lambda m: dict(
                firstName=User.objects.get(id=m.user_id).first_name, 
                lastName=User.objects.get(id=m.user_id).last_name
            ), memberships)

            #AA:TODO: extend member details to show more about each member. Maybe 
            # another query from app may be required for drill-down details
            self.response.add_data("Members", members)
            self.response.add_data("Count", count)
            self.response.add_data("CreatorID", table.creator.id) 

        return self.response

    
    def UserGetDetail(self):
	return self.response

    def TableCreate(self):
	if self.lat == None and self.lng == None:
	    try:
	        self.lat = self.userprofile.location.get().lat
		self.lng = self.userprofile.location.get().lng
	    except:
                #maybe location timedout. Shouldn't happen if messages from app
                #are coming correctly...
                print ' No location information available'
		return self.response

        tablename = self.sender['table_name']
        secure = self.sender['secureTable']
        if self.sender.has_key('lifetime'):
            lifetime = self.sender['lifetime'] if self.sender['lifetime'] else settings.WIZCARD_DEFAULT_TABLE_LIFETIME
        else:
            lifetime = settings.WIZCARD_DEFAULT_TABLE_LIFETIME

        if secure:
            password = self.sender['password']
        else:
            password = ""
        table = VirtualTable.objects.create(tablename=tablename, secureTable=secure, 
                                            password=password, creator=self.user, 
                                            life_time=lifetime)
        
        #TODO: AA handle create failure and/or unique name enforcement
        #update location in ptree
        #AA:TODO move create to overridden create in VirtualTable
        table.create_location(self.lat, self.lng)
        l = table.location.get()
	l.start_timer(lifetime)
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

        if table.isSecure():
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
            table.delete(type=Notification.WIZ_TABLE_DESTROY)
        else:
            self.response.error_response(err.NOT_AUTHORIZED)

        return self.response


    def TableRename(self):
        old_name = self.sender['old_name']
        new_name = self.sender['new_name']
        table_id = self.sender['tableID']

        try:
            table = VirtualTable.objects.get(id=table_id)
	    if table.creator != self.user:
		self.response.error_response(err.NOT_AUTHORIZED)
		return self.response
	    if old_name != table.tablename:
		self.response.error_response(err.NAME_ERROR)
		return self.response
	        
            table.tablename = new_name
            table.save()
            self.response.add_data("tableID", table.pk)
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            #shouldn't/couldn't happen
        
	return self.response

VALIDATOR = 0
HANDLER = 1



wizrequest_handler = WizRequestHandler.as_view()
#wizconnection_request = login_required(WizConnectionRequestView.as_view())
