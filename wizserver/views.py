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
import datetime
import random
from django.core.cache import cache
from django.conf import settings
from nexmomessage import NexmoMessage
import colander
from wizcard import message_format as message_format


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

class ParseMsgAndDispatch:
    def __init__(self, request):
        #validate header
        self.header = Header(request)

    def dispatch(self):
        response = self.header.prepare()
	if response:
            return response
	return self.header.process()

    def dummy_validator(self, req):
        return req

    def securityException(self):
	#AA TODO
	print 'ALERT ALERT!! FIXME'
	return None
	

class Header(ParseMsgAndDispatch):
    def __init__(self, request):
        #invoke the appropriate handler based on message type
        #raw message self.request = req
        #json deserialized
        self.request = request
        self.msg = json.loads(request.body)
        self.handler_cls = None
        self.msg_type = None

    def __repr__(self):
        return str(self.msg)

    def prepare(self):
        try:
            #self.header = message_format.CommonHeaderSchema().deserialize(self.msg['header'])
            self.header = self.msg['header']
        except colander.Invalid:
            response = Response()
            response.ignore()
            return response

	self.msg_type = self.header['msgType']
        print 'received message', self.msg_type
	handler = msgTypesValidatorsAndHandlers[self.msg_type][message_format.HANDLER]
	#validator = msgTypesValidatorsAndHandlers[self.msg_Type][message_format.VALIDATOR]
	validator = self.dummy_validator
        self.handler_cls = handler(self.msg, validator, self.request)
	response = self.handler_cls.prepare()
	if response:
	    return response

        #AA:TODO Do the user validation here
        if not self.msg_is_initial() and self.validateIncomingMessage():
            self.securityException()
            response.ignore()
            return response

        #update location since it may have changed
        if self.msg_has_location(self.handler_cls):
            #user is kosher (one hopes) here
                    self.handler_cls.user.profile.create_or_update_location(
                            self.handler_cls.lat,
                            self.handler_cls.lng)

        #make the user as alive
        if not self.msg_is_initial():
	    now = datetime.datetime.now()
	    cache.set('seen_%s' % (self.handler_cls.user), now, 
		    settings.USER_LASTSEEN_TIMEOUT)

    def process(self):
        print self
	return self.handler_cls.process()

    def msg_has_location(self, cls):
        return hasattr(cls, 'lat') and hasattr(cls, 'lng') and self.msg_type not in ['signup', 'login', 'register', 'current_location']

    def msg_is_initial(self):
	return self.msg_type in ['signup', 'login', 'register', 'phone_check_req', 'phone_check_resp']
     
    def validateIncomingMessage(self):
        if self.handler_cls.sender.has_key('userID') and self.handler_cls.sender.has_key('wizUserID'):
                try:
                    username = self.sender['userID']
                    wizUserID = self.sender['wizUserID']
                    user = User.objects.get(username=username, id=wizUserID)
                except:
                    return False
        if self.request.user.username != self.handler_cls.user.username:
            return False

        return True

    def securityException(self):
        #AA: TODO
        print 'ALERT ALERT ALERT'
        return None

class SignUp(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
        #req : Original http req/body
        #msg : json serialized body - Wizcard portion of message
        self.request = req
	self.msg = msg
	self.validator = validator
	self.response = Response()

    def prepare(self):
        try:
            self.des = self.validator(self.msg)
        except colander.Invalid:
            self.response.ignore()
            return self.response
        self.sender = self.des['sender']

    def process(self):
        email = self.sender['email']
	username = email
	password = "wizard"

	user = User.objects.create_user(username, email, password)
	user.set_password(password)
	user.save()

	#generate a uniue userid
	user.profile.userid = UserProfile.objects.id_generator()
	user.profile.save()

	user = authenticate(username=username, password=password)
	login(self.request, user)

	#update location in ptree
	if self.sender.has_key('lat') and self.sender.has_key('lng'):
            user.profile.create_or_update_location(self.sender['lat'], self.sender['lng'])

        self.response.add_data("wizUserID", user.pk)
        self.response.add_data("userID", user.profile.userid)

        return self.response

class Login(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
        #req : Original http req/body
        #msg : json serialized body - Wizcard portion of message
        self.request = req
	self.msg = msg
	self.validator = validator
	self.response = Response()

    def prepare(self):
        try:
            des = self.validator(self.msg)
	    self.sender = des['sender']
            try:
                username = self.sender['email']
		self.user = User.objects.get(username=username)
            except ObjectDoesNotExist:
                self.response.error_response(err.USER_DOESNT_EXIST)
		return self.response
        except colander.Invalid:
	    self.response.ignore()
	return self.response
            
    def process(self):
        do_sync = False
        #cross verify userID
        try:
            w_userid = self.sender['userID']
            #take this out for now...need to figure out ios app's userid
            if not self.sender['userID'] == self.user.profile.userid:
                pass
                #self.response.error_response(errno=1, errorStr="invalid user")
                #return self.response
        except:
            do_sync = True

        #password = self.sender['pasword']
        password = "wizard"
        authenticate(username=username, password=password)
        if not self.user.is_authenticated():
            self.response.error_response(err.AUTHENTICATION_FAILED)
            return self.response
        login(self.request, self.user) 

        if do_sync:
            #sync  all syncables
            s = profile.serialize_objects()
	    if s.has_key('wizcard'):
                self.response.add_data("wizcards", s['wizcard'])
		if s.has_key('wizconnections'):
                    self.response.add_data("rolodex", s['wizconnections'])
		if s.has_key('wizcard_flicks'):
                    self.response.add_data("wizcard_flicks", s['wizcard_flicks'])
		if s.has_key('tables'):
                    self.response.add_data("tables", s['tables'])

        return self.response

class PhoneCheckRequest(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
	self.msg = msg
	self.validator = validator
	self.response = Response()

    def prepare(self):
        try:
            des = self.validator(msg)
        except colander.Invalid:
            self.response.ignore()
	    return self.response
        self.sender = des['sender']

    def process(self):
	user_id = self.sender['userID']
	response_mode = self.sender['checkMode']
	response_target = self.sender['target']

	k_user = (settings.PHONE_CHECK_USER_KEY % user_id)
	k_rand = (settings.PHONE_CHECK_USER_RAND_KEY % user_id)
	k_retry = (settings.PHONE_CHECK_USER_RETRY_KEY % user_id)

	user = cache.get(k_user)
	if user:
	    #should not be. Lets just clear it
	    cache.delete(k_user)

        d = dict()
	#new req, generate random num
	d[k_user] = user_id
	d[k_rand] = random.randint(settings.PHONE_CHECK_RAND_LOW, settings.PHONE_CHECK_RAND_HI)
	d[k_retry] = 1
	cache.set_many(d, timeout=settings.PHONE_CHECK_TIMEOUT)

	if response_mode == "voice":
	    #TODO
	    pass

        #send a text with the rand
        msg = settings.PHONE_CHECK_MESSAGE
        msg['to'] = response_target
        msg['text'] = settings.PHONE_CHECK_RESPONSE_GREETING % d[k_rand]
        sms = NexmoMessage(msg)
        sms.set_text_info(msg['text'])
        response = sms.send_request()
        if response['messages'][0]['status'] != '0':
            #some error...let the app know
            return self.response.error_response(err.NEXMO_SMS_SEND_FAILED)

        #TOD: Don' forget to remove this
        self.response.add_data("key", d[k_rand])
        return self.response
	
class PhoneCheckResponse(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
	self.msg = msg
	self.validator = validator
        self.response = Response()

    def prepare(self):
        try:
            self.des = self.validator(self.msg)
        except colander.Invalid:
            self.response.ignore()
            return self.response
        self.sender = self.des['sender']

    def process(self):
	user_id = self.sender['userID']
	challenge_response = self.sender['responseKey']
	if not (user_id and challenge_response):
            return self.response.error_response(err.PHONE_CHECK_CHALLENGE_RESPONSE_DENIED)

	k_user = (settings.PHONE_CHECK_USER_KEY % user_id)
	k_rand = (settings.PHONE_CHECK_USER_RAND_KEY % user_id)
	k_retry = (settings.PHONE_CHECK_USER_RETRY_KEY % user_id)

	d = cache.get_many([k_user, k_rand, k_retry])

	if d[k_retry] > settings.MAX_PHONE_CHECK_RETRIES:
	    cache.delete(k_user)
            return self.response.error_response(err.PHONE_CHECK_RETRY_EXCEEDED)

        cache.incr(k_retry)
	if challenge_response != d[k_rand]:
            return self.response.error_response(err.PHONE_CHECK_CHALLENGE_RESPONSE_DENIED)

        #response is valid. all done. #clear cache
	cache.delete_many([k_user, k_rand, k_retry])
	    
        return self.response

class Register(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
        self.request = req
	self.msg = msg
	self.validator = validator
	self.response = Response()

    def prepare(self):
        try:
            self.des = self.validator(self.msg)
        except colander.Invalid:
            self.response.ignore()
            return self.response
        self.sender = self.des['sender']
        try:
            self.lat = self.sender['lat']
            self.lng = self.sender['lng']
        except:
            pass

    def process(self):
        print '{sender} at location [{locX} , {locY}] sent '.format (sender=self.sender['userID'], locX=self.sender['lat'], locY=self.sender['lng'])

        wizcard_s = None
        rolodex_s = None

        do_sync = False
        w_count = 0
        r_count = 0

        try:
            first_name = self.sender['first_name']
        except:
            first_name = ""

        try:
            last_name = self.sender['last_name']
        except:
            last_name = ""

        try:
            email = self.sender['email']
        except:
            email = ""

        try:
            l_userid = self.sender['userID'] 
	except KeyError:
	    #malicious handling
	    return self.securityException()

        password = "wizard"
        #password = self.sender['password']

        try: 
            w_userid = self.sender['wizUserID']
            #existing user
	    try:
                user = User.objects.get(id=w_userid, username=l_userid)
	    except ObjectDoesNotExist:
		return self.securityException()
        except KeyError:
            #create case or sync case
            user, created = User.objects.get_or_create(username=l_userid,
                                                       defaults={'first_name':first_name,
                                                                 'last_name':last_name,
                                                                 'email':email})
            if not created:
		do_sync = True
	    else:
                user.set_password(password)
		user.save()

        user = authenticate(username=l_userid, password=password)
        if not user.is_authenticated():
            self.response.error_response(err.AUTHENTICATION_FAILED)
            return self.response

        # Correct password, and the user is marked "active"
        login(self.request, user)

        #sync the app from server
        profile = user.profile

        #fill in device details
        try:
            profile.device_type = self.sender['deviceType']
        except:
            pass
        try:
            profile.device_id = self.sender['deviceID']
        except:
            pass
        try:
            profile.reg_token = self.sender['reg_token']
        except:
            pass

        profile.save()

        if do_sync:
            #sync all syncables
            s = profile.serialize_objects()
	    if s.has_key('wizcard'):
                self.response.add_data("wizcards", s['wizcard'])
		if s.has_key('wizconnections'):
                    self.response.add_data("rolodex", s['wizconnections'])
		if s.has_key('wizcard_flicks'):
                    self.response.add_data("wizcard_flicks", s['wizcard_flicks'])
		if s.has_key('tables'):
                    self.response.add_data("tables", s['tables'])

        #update location in ptree
        profile.create_or_update_location(self.sender['lat'], self.sender['lng'])

        self.response.add_data("wizUserID", user.pk)
        if wizcard_s:
            self.response.add_data("wizcards", wizcard_s)
        if rolodex_s:
            self.response.add_data("rolodex", rolodex_s)

        return self.response

class LocationUpdate(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
	self.msg = msg
	self.validator = validator
	self.response = Response()

    def prepare(self):
        try:
            self.des = self.validator(self.msg)
        except colander.Invalid:
            self.response.ignore()
            return self.response
        self.sender = self.des['sender']
	try:
	    self.user = User.objects.get(id=self.sender['wizUserID'])
	except: 
            self.response.error_response(err.USER_DOESNT_EXIST)
	    return self.response
        self.lat = self.sender['lat']
	self.lng = self.sender['lng']

    def process(self):
        profile = self.user.profile
        #update location in ptree
        profile.create_or_update_location(self.lat, self.lng)
        return self.response

class NotificationsGet(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
	self.msg = msg
	self.validator = validator
        self.response = Response()

    def prepare(self):
        try:
            self.des = self.validator(self.msg)
        except colander.Invalid:
            self.response.ignore()
            return self.response
        self.sender = self.des['sender']
	try:
	    self.user = User.objects.get(id=self.sender['wizUserID'])
	except: 
            self.response.error_response(err.USER_DOESNT_EXIST)
	    return self.response
        try:
            self.lat = self.sender['lat']
	    self.lng = self.sender['lng']
        except:
	    try:
	        self.lat = self.user.profile.location.get().lat
		self.lng = self.user.profile.location.get().lng
	    except:
                #maybe location timedout. Shouldn't happen if messages from app
                #are coming correctly...
		return self.response

    def process(self):
        #AA: TODO: Change this to get userId from session
        notifications = Notification.objects.unread(self.user)
        notifResponse = NotifResponse(notifications)

        #any wizcards dropped nearby
        try:
            lat = self.sender['lat']
            lng = self.sender['lng']
        except:
            try:
                lat = self.user.profile.location.get().lat
                lng = self.user.profile.location.get().lng
            except:
                #maybe location timedout. Shouldn't happen if messages from app
                #are coming correctly...
                return notifResponse.response

        #AA:TODO: Use come caching framework to cache these
        flicked_wizcards, count = WizcardFlick.objects.lookup(
                lat, 
                lng, 
                settings.DEFAULT_MAX_LOOKUP_RESULTS)
        if count and not self.user.profile.is_ios():
            notifResponse.notifFlickedWizcardsLookup(count, 
                    self.user, flicked_wizcards)

        users, count = self.user.profile.lookup(settings.DEFAULT_MAX_LOOKUP_RESULTS)
        if count and not self.user.profile.is_ios():
            notifResponse.notifUserLookup(count, users)

        #tables is a smaller entity...get the tables as well instead of just count
        tables, count = VirtualTable.objects.lookup(
                lat, 
                lng, 
                settings.DEFAULT_MAX_LOOKUP_RESULTS)
        if count and not self.user.profile.is_ios():
            notifResponse.notifTableLookup(count, self.user, tables)

        Notification.objects.mark_all_as_read(self.user)

        #tickle the timer to keep it going and update the location if required 
        self.user.profile.create_or_update_location(lat, lng)
        return notifResponse

class WizcardEdit(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
	self.msg = msg
	self.validator = validator
	self.response = Response()

    def prepare(self):
        try:
            self.des = self.validator(self.msg)
        except colander.Invalid:
            self.response.ignore()
            return self.response
        self.sender = self.des['sender']
	try:
	    self.user = User.objects.get(id=self.sender['wizUserID'])
	except: 
            self.response.error_response(err.USER_DOESNT_EXIST)
	    return self.response

    def process(self):
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

        if self.sender.has_key('first_name'):
            first_name = self.sender['first_name']
            if wizcard.first_name != first_name:
                wizcard.first_name = first_name
                modify = True
        if self.sender.has_key('last_name'):
            last_name = self.sender['last_name']
            if wizcard.last_name != last_name:
                wizcard.last_name = last_name
                modify = True
        if self.sender.has_key('company'):
            company = self.sender['company']
            if wizcard.company != company:
                wizcard.company = company
                modify = True
        if self.sender.has_key('title'):
            title = self.sender['title']
            if wizcard.title != title:
                wizcard.title = title
                modify = True
            wizcard.title = title
            modify = True
        if self.sender.has_key('phone2'):
            phone2 = self.sender['phone2']
            if wizcard.phone2 != phone2:
                wizcard.phone2 = phone2
                modify = True
        if self.sender.has_key('email'):
            email = self.sender['email']
            if wizcard.email != email:
                wizcard.email = email
                modify = True
        if self.sender.has_key('address_street1'):
            street1 = self.sender['address_street1']
            if wizcard.address_street1 != street1:
                wizcard.address_street1 = street1
                modify = True
        if self.sender.has_key('address_city'):
            city = self.sender['address_city']
            if wizcard.address_city != city:
                wizcard.address_city = city
                modify = True
        if self.sender.has_key('address_state'):
            state = self.sender['address_state']
            if wizcard.address_state != state:
                wizcard.address_state = state
                modify = True
        if self.sender.has_key('address_country'):
            country = self.sender['address_country']
            if wizcard.address_country != country:
                wizcard.address_country = country
                modify = True
        if self.sender.has_key('address_zip'):
            zipcode = self.sender['address_zip']
            if wizcard.address_zip != zipcode:
                wizcard.address_zip = zipcode
                modify = True

        if self.sender.has_key('thumbnailImage') and self.sender['imageWasEdited']:
            rawimage = bytes(self.sender['thumbnailImage'])
            upfile = SimpleUploadedFile("%s-%s.jpg" % (wizcard.pk, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")), rawimage, "image/jpeg")
            wizcard.thumbnailImage.save(upfile.name, upfile) 
            modify = True

        if self.sender.has_key('VideoUrl'):
            rawvideo = self.sender['VideoUrl']
            upfile = SimpleUploadedFile("%s-%s.mp4" % (wizcard.pk, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")), rawvideo, "video/mp4")
            wizcard.video.save(upfile.name, upfile) 
            modify = True

        if self.sender.has_key('contact_container'):
            contactContainerList = self.sender['contact_container']
            wizcard.contact_container.all().delete()
            modify = True

            for contactItems in contactContainerList:
                if contactItems.has_key('title'):
                    title = contactItems['title']
                else:
                    title = ""
                if contactItems.has_key('company'):
                    company = contactItems['company']
                else:
                    company = ""
                ContactContainer(wizcard=wizcard, title=title, company=company).save()

        #flood to contacts
        if modify:
            wizcard.save()
            wizcard.flood()

        self.response.add_data("wizCardID", wizcard.pk)

        return self.response

class WizcardAccept(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
	self.msg = msg
	self.validator = validator
	self.response = Response()

    def prepare(self):
        try:
            self.des = self.validator(self.msg)
        except colander.Invalid:
            self.response.ignore()
            return self.response
        self.sender = self.des['sender']
        self.receiver = self.des['receiver']
	try:
	    self.user = User.objects.get(id=self.sender['wizUserID'])
	    self.r_user = User.objects.get(id=self.receiver['wizUserID'])
	except: 
            self.response.error_response(err.USER_DOESNT_EXIST)
	    return self.response

    def process(self):
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

class WizConnectionRequestDecline(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
	self.msg = msg
	self.validator = validator
        self.response = Response()

    def prepare(self):
        try:
            self.des = self.validator(self.msg)
        except colander.Invalid:
            self.response.ignore()
            return self.response
        self.sender = self.des['sender']
        self.receiver = self.des['receiver']
	try:
	    self.user = User.objects.get(id=self.sender['wizUserID'])
	    self.r_user = User.objects.get(id=self.receiver['wizUserID'])
	except: 
            self.response.error_response(err.USER_DOESNT_EXIST)
	    return self.response

    def process(self):
        try:
            wizcard1 = self.user.wizcard
            wizcard2 = self.r_user.wizcard
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        #wizcard2 must have sent a wizconnection_request, lets clear it
        Wizcard.objects.wizconnection_req_clear(wizcard2, wizcard1)

        #Q a notif to other guy so that the app on the other side can react
        notify.send(self.user, recipient=self.r_user,
                    verb='revoked wizcard', target=wizcard1)

        return self.response

class WizcardRolodexDelete(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
	self.msg = msg
	self.validator = validator
        self.response = Response()

    def prepare(self):
        try:
            self.des = self.validator(self.msg)
        except colander.Invalid:
            self.response.ignore()
            return self.response
        self.sender = self.des['sender']
        self.receiver = self.des['receiver']
	try:
	    self.user = User.objects.get(id=self.sender['wizUserID'])
	    self.r_user = User.objects.get(id=self.receiver['wizUserID'])
	except: 
            self.response.error_response(err.USER_DOESNT_EXIST)
	    return self.response

    def process(self):
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

class WizCardFlick(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
	self.msg = msg
	self.validator = validator
        self.response = Response()

    def prepare(self):
        try:
            self.des = self.validator(self.msg)
        except colander.Invalid:
            self.response.ignore()
            return self.response
        self.sender = self.des['sender']
	try:
	    self.user = User.objects.get(id=self.sender['wizUserID'])
	except: 
            self.response.error_response(err.USER_DOESNT_EXIST)
	    return self.response

    def process(self):
        try:
            wizcard = self.user.wizcard
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response
        try:
            flick_timeout = self.sender['flickTimeout']
        except:
            flick_timeout = settings.WIZCARD_FLICK_DEFAULT_TIMEOUT

        try:
            lat = self.user.profile.location.get().lat
	    lng = self.user.profile.location.get().lng
	except:
	    #should not happen since app is expected to send a register or something
	    #everytime it wakes up...however, network issues can cause app to go offline 
	    #while still in foreground. No option but to send back error response to app
	    #However, if app had included location information, then we will update_location
	    #before getting here and be ok
            self.response.error_response(err.LOCATION_UNKNOWN)
	    return self.response
        
	flick_card = wizcard.check_flick_duplicates(lat, lng)

	if flick_card:
	    flick_card.location.get().reset_timer()
        else:
	    flick_card = WizcardFlick.objects.create(wizcard=wizcard, lat=lat, lng=lng)
            location = flick_card.create_location(lat, lng)
            location.start_timer(flick_timeout)

        self.response.add_data("flickCardID", flick_card.pk)
        return self.response

class WizcardFlickAccept(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
	self.msg = msg
	self.validator = validator
        self.response = Response()

    def prepare(self):
        try:
            self.des = self.validator(self.msg)
        except colander.Invalid:
            self.response.ignore()
            return self.response
        self.sender = self.des['sender']
        self.receiver = self.des['receiver']
	try:
	    self.user = User.objects.get(id=self.sender['wizUserID'])
	    self.r_user = User.objects.get(id=self.receiver['wizUserID'])
	except: 
            self.response.error_response(err.USER_DOESNT_EXIST)
	    return self.response

    def process(self):
        try:
            wizcard1 = self.user.wizcard
            wizcard2 = self.r_user.wizcard
        except:
            try:
                wizcard1 = Wizcard.objects.get(id=self.sender['wizCardID'])
                wizcard2 = Wizcard.objects.get(id=self.receiver['wizCardID'])
            except:
                self.response.error_response(err.OBJECT_DOESNT_EXIST)
                return self.response

	#create a wizconnection and then accept it
	Wizcard.objects.exchange(wizcard1, wizcard2, True)

        return self.response

class WizcardSendToContacts(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
	self.msg = msg
	self.validator = validator
        self.response = Response()

    def prepare(self):
        try:
            self.des = self.validator(self.msg)
        except colander.Invalid:
            self.response.ignore()
            return self.response
        self.sender = self.des['sender']
        self.receiver = self.des['receiver']
	try:
	    self.user = User.objects.get(id=self.sender['wizUserID'])
	except: 
            self.response.error_response(err.USER_DOESNT_EXIST)
	    return self.response

    def process(self):
        #implicitly create a bidir cardship (since this is from contacts)
        #and also Q the other guys cards here
        count = 0
        try:
            wizcard1 = self.user.wizcard
        except ObjectDoesNotExist:
	    self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        #A:TODO: Cross verify user agains wizcard
        contacts = self.receiver['contacts']
        for contact in contacts:
            try:
                #AA:TODO: phone should just be the mobile phone. App needs to change
                # to adjust this. Also, array is not required
                phones = contact['phone']
                for phone in phones:
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
                #AA:TODO: what to do ?
	        self.response.error_response(err.INTERNAL_ERROR)

        self.response.add_data("count", count)
        return self.response

class WizcardSendUnTrusted(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
	self.msg = msg
	self.validator = validator
        self.response = Response()

    def prepare(self):
        try:
            self.des = self.validator(self.msg)
        except colander.Invalid:
            self.response.ignore()
            return self.response
        self.sender = self.des['sender']
        self.receivers = self.des['receiver']['wizUserIDs']
	try:
	    self.user = User.objects.get(id=self.sender['wizUserID'])
	except: 
            self.response.error_response(err.USER_DOESNT_EXIST)
	    return self.response

    def process(self):
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

class WizcardSendToFutureContacts(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
	self.msg = msg
	self.validator = validator
	self.response = Response()
        self.phones = phones
        self.sender = sender

    def prepare(self):
        try:
            self.des = self.validator(self.msg)
        except colander.Invalid:
            self.response.ignore()
            return self.response
        self.sender = self.des['sender']

    def process(self):
        for phone in self.phones:
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

class UserQueryByLocation(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
	self.msg = msg
	self.validator = validator
	self.response = Response()

    def prepare(self):
        try:
            self.des = self.validator(self.msg)
        except colander.Invalid:
            self.response.ignore()
            return self.response
        self.sender = self.des['sender']
	try:
	    self.user = User.objects.get(id=self.sender['wizUserID'])
	except: 
            self.response.error_response(err.USER_DOESNT_EXIST)
	    return self.response

    def process(self):
        profile = self.user.profile
        #update location in ptree
        profile.create_or_update_location(self.sender['lat'], 
                                          self.sender['lng'])
        lookup_result, count = profile.lookup(settings.DEFAULT_MAX_LOOKUP_RESULTS)
        if count:
            users_s = UserProfile.objects.serialize(lookup_result)
            self.response.add_data("queryResult", users_s)
            self.response.add_data("count", count)
	else:
            self.response.error_response(err.NONE_FOUND)

        return self.response

class UserQueryByName(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
	self.msg = msg
	self.validator = validator
	self.response = Response()

    def prepare(self):
        try:
            self.des = self.validator(self.msg)
        except colander.Invalid:
            self.response.ignore()
            return self.response
        self.sender = self.des['sender']
        self.receiver = self.des['receiver']
	try:
	    self.user = User.objects.get(id=self.sender['wizUserID'])
	except: 
            self.response.error_response(err.USER_DOESNT_EXIST)
	    return self.response

    def process(self):
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

        result, count = Wizcard.objects.find_users(self.user, name, phone, email)
        #send back to app for selection

        if (count):
            users = serialize(result, **fields.wizcard_user_query_template)
            self.response.add_data("queryResult", users)
            self.response.add_data("count", count)
	else:
            self.response.error_response(err.NONE_FOUND)
 
        return self.response

class TableQuery(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
	self.msg = msg
	self.validator = validator
        self.response = Response()

    def prepare(self):
        try:
            self.des = self.validator(self.msg)
        except colander.Invalid:
            self.response.ignore()
            return self.response
        self.sender = self.des['sender']
	try:
	    self.user = User.objects.get(id=self.sender['wizUserID'])
	except: 
            self.response.error_response(err.USER_DOESNT_EXIST)
	    return self.response

    def process(self):
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
        else:
            self.response.error_response(err.NONE_FOUND)

        return self.response

class TableDetails(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
	self.msg = msg
	self.validator = validator
        self.response = Response()

    def prepare(self):
        try:
            self.des = self.validator(self.msg)
        except colander.Invalid:
            self.response.ignore()
            return self.response
        self.sender = self.des['sender']
	try:
	    self.user = User.objects.get(id=self.sender['wizUserID'])
	except: 
            self.response.error_response(err.USER_DOESNT_EXIST)
	    return self.response

    def process(self):
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

class TableCreate(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
	self.msg = msg
	self.validator = validator
        self.response = Response()

    def prepare(self):
        try:
            self.des = self.validator(self.msg)
        except colander.Invalid:
            self.response.ignore()
            return self.response
        self.sender = self.des['sender']
	try:
	    self.user = User.objects.get(id=self.sender['wizUserID'])
	except: 
            self.response.error_response(err.USER_DOESNT_EXIST)
	    return self.response
        try:
            self.lat = self.sender['lat']
            self.lng = self.sender['lng']
        except:
            pass

    def process(self):
        tablename = self.sender['table_name']
        secure = self.sender['secureTable']
        #lifetime = self.sender['lifetime']
        lifetime = 1
        if not lifetime:
            lifetime = 30
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

class TableJoin(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
	self.msg = msg
	self.validator = validator
        self.response = Response()

    def prepare(self):
        try:
            self.des = self.validator(self.msg)
        except colander.Invalid:
            self.response.ignore()
            return self.response
        self.sender = self.des['sender']
	try:
	    self.user = User.objects.get(id=self.sender['wizUserID'])
	except: 
            self.response.error_response(err.USER_DOESNT_EXIST)
	    return self.response

    def process(self):
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
            password = ""
        
        joined = table.join_table_and_exchange(self.user, password, True)

        if joined is None:
            self.response.error_response(err.AUTHENTICATION_FAILED)
        else:
            self.response.add_data("tableID", joined.pk)
        return self.response

class TableLeave(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
	self.msg = msg
	self.validator = validator
        self.response = Response()

    def prepare(self):
        try:
            self.des = self.validator(self.msg)
        except colander.Invalid:
            self.response.ignore()
            return self.response
        self.sender = self.des['sender']
	try:
	    self.user = User.objects.get(id=self.sender['wizUserID'])
	except: 
            self.response.error_response(err.USER_DOESNT_EXIST)
	    return self.response

    def process(self):
        try:
            table = VirtualTable.objects.get(id=self.sender['tableID'])
            leave = table.leave_table(self.user)
            self.response.add_data("tableID", leave.pk)
        except:
            pass

        return self.response

class TableDestroy(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
	self.msg = msg
	self.validator = validator
        self.response = Response()

    def prepare(self):
        try:
            self.des = self.validator(self.msg)
        except colander.Invalid:
            self.response.ignore()
            return self.response
        self.sender = self.des['sender']
	try:
	    self.user = User.objects.get(id=self.sender['wizUserID'])
	except: 
            self.response.error_response(err.USER_DOESNT_EXIST)
	    return self.response

    def process(self):
        try:
            table = VirtualTable.objects.get(id=self.sender['tableID'])
        except ObjectDoesNotExist:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            return self.response

        if table.creator == self.user:
            table.delete()
        else:
            self.response.error_response(err.NOT_AUTHORIZED)

        return self.response

class TableRename(ParseMsgAndDispatch):
    def __init__(self, msg, validator, req=None):
	self.msg = msg
	self.validator = validator
        self.response = Response()

    def prepare(self):
        try:
            self.des = self.validator(self.msg)
        except colander.Invalid:
            self.response.ignore()
            return self.response
        self.sender = self.des['sender']
	try:
	    self.user = User.objects.get(id=self.sender['wizUserID'])
	except: 
            self.response.error_response(err.USER_DOESNT_EXIST)
	    return self.response

    def process(self):
        tablename = self.sender['table_name']
        table_id = self.sender['tableID']

        try:
            table = VirtualTable.objects.get(id=table_id)
	    if table.creator != self.user:
		self.response.error_response(err.NOT_AUTHORIZED)
		return self.response
            table.tablename = tablename
            table.save()
            self.response.add_data("tableID", table.pk)
            self.response.add_data("tableID", table.pk)
        except:
            self.response.error_response(err.OBJECT_DOESNT_EXIST)
            #shouldn't/couldn't happen
        
	return self.response

msgTypesValidatorsAndHandlers = {
    'signup'                      : (message_format.SignupSchema, SignUp),
    'login'                       : (message_format.LoginSchema, Login),
    'phone_check_req'             : (message_format.PhoneCheckRequestSchema, PhoneCheckRequest),
    'phone_check_rsp'             : (message_format.PhoneCheckResponseSchema, PhoneCheckResponse),
    'register'                    : (message_format.RegisterSchema,Register),
    'current_location'            : (message_format.LocationUpdateSchema, LocationUpdate),
    'get_cards'                   : (message_format.NotificationsGetSchema, NotificationsGet),
    'edit_card'                   : (message_format.WizcardEditSchema, WizcardEdit),
    'add_notification_card'       : (message_format.WizcardAcceptSchema, WizcardAccept),
    'delete_notification_card'    : (message_format.WizConnectionRequestDeclineSchema, WizConnectionRequestDecline),
    'delete_rolodex_card'         : (message_format.WizcardRolodexDeleteSchema, WizcardRolodexDelete),
    'card_flick'                  : (message_format.WizcardFlickSchema, WizCardFlick),
    'card_flick_accept'           : (message_format.WizcardFlickAcceptSchema, WizcardFlickAccept),
    'send_card_to_contacts'       : (message_format.WizcardSendToContactsSchema, WizcardSendToContacts),
    'send_card_to_user'           : (message_format.WizcardSendUnTrustedSchema, WizcardSendUnTrusted),
    'send_card_to_future_contacts': (message_format.WizcardSendToFutureContactsSchema, WizcardSendToFutureContacts),
    'find_users_by_location'      : (message_format.UserQueryByLocationSchema, UserQueryByLocation),
    'send_query_user'             : (message_format.UserQueryByNameSchema, UserQueryByName),
    'show_table_list'             : (message_format.TableQuerySchema, TableQuery),
    'table_details'               : (message_format.TableDetailsSchema, TableDetails),
    'create_table'                : (message_format.TableCreateSchema, TableCreate),
    'join_table'                  : (message_format.TableJoinSchema, TableJoin),
    'leave_table'                 : (message_format.TableLeaveSchema, TableLeave),
    'destroy_table'               : (message_format.TableDestroySchema, TableDestroy),
    'rename_table'                : (message_format.TableRenameSchema, TableRename)
}


wizrequest_handler = WizRequestHandler.as_view()
#wizconnection_request = login_required(WizConnectionRequestView.as_view())

