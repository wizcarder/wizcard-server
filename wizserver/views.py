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
from location_mgr.models import LocationMgr
import msg_test, fields
import datetime
from django.core.cache import cache
from django.conf import settings



#logger = logging.getLogger(__name__)

class WizRequestHandler(View):
    parsed_msg = {}

    def get(self, request, *args, **kwargs):
        message = msg_test.get_cards1
        #msg = json.loads(message)

        # process request
        ret = self.processIncomingMessage(message)
        #send response
        return HttpResponse(json.dumps(ret))

    def test(self, request):
        return HttpResponse("ok")

    def post(self, request, *args, **kwargs):
        self.request = request

        # Dispatch to appropriate message handler
        pdispatch = ParseMsgAndDispatch(request)
        ret =  pdispatch.processIncomingMessage()
        #send response
        return HttpResponse(json.dumps(ret))


class ParseMsgAndDispatch:
    def __init__(self, request):
        self.request = request
        msg = json.loads(self.request.body)
        self.header = msg['header']
        self.sender = msg['sender']
        try:
            self.receiver = msg['receiver']
        except:
            pass
        self.msgType = self.header['msgType']

        print '{sender} sent "{type}"'.format (sender=self.sender['userID'], type=self.header['msgType'])

        self.response = Response()

    def processIncomingMessage(self):
        msgHandlers = {
            'signup'                        : self.processSignUp,
            'login'                         : self.processLogin,
            'register'                      : self.processRegister,
            #'add_card'                      : self.processAddWizcard,
            'edit_card'                     : self.processModifyWizcard,
            #'delete_card'                   : self.processDeleteWizcardOwn,
            'delete_notification_card'      : self.processDeleteWizcardNotification,
            'delete_rolodex_card'           : self.processDeleteWizcardRolodex,
            'current_location'              : self.processLocationUpdate,
            'add_notification_card'         : self.processAcceptCard,
            'add_flicked_card'         	    : self.processAcceptFlickedCard,
            'card_flick'                    : self.processWizcardFlick,
            'get_cards'                     : self.processGetNotifications,
            'send_card_to_contacts'         : self.processSendCardToContacts,
            'send_card_to_future_contacts'  : self.processSendCardToFutureContacts,
            'send_card_to_user'             : self.processSendCardUC,
            'send_query_user'               : self.processQueryUserByName,
            'find_users_by_location'        : self.processQueryUserByLocation,
            'show_table_list'               : self.processQueryTable,
            'table_details'                 : self.processGetTableDetails,
            'create_table'                  : self.processCreateTable,
            'join_table'                    : self.processJoinTable,
            'leave_table'                   : self.processLeaveTable,
            'destroy_table'                 : self.processDestroyTable
        }

        self.update_location(self.msgType)

        # Dispatch to appropriate message handler
        retval =  msgHandlers[self.msgType]()

        #do the user tracking here
        if not self.response.is_error_response():
            current_user = self.request.user
            now = datetime.datetime.now()
            cache.set('seen_%s' % (current_user.username), now, 
                      settings.USER_LASTSEEN_TIMEOUT)

        return retval

    def processSignUp(self):
        email = self.sender['email']
        username = email
        #password = self.sender['password']
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
        try:
            lat = self.sender['lat']
            lng = self.sender['lng']
            user.profile.create_or_update_location(self.sender['lat'], 
                                                   self.sender['lng'])
        except:
            pass

        self.response.add_data("wizUserID", user.pk)
        self.response.add_data("userID", user.profile.userid)
        return self.response.response

    def processLogin(self):
        do_sync = False
        try:
            username = self.sender['email']
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            self.response.error_response(errno=1, errorStr="invalid username or password")
            return self.response.response

        #cross verify userID
        try:
            w_userid = self.sender['userID']
            #take this out for now...need to figure out ios app's userid
            if not self.sender['userID'] == user.profile.userid:
                pass
                #self.response.error_response(errno=1, errorStr="invalid user")
                #return self.response.response
        except:
            do_sync = True

        #password = self.sender['pasword']
        password = "wizard"
        user = authenticate(username=username, password=password)
        if not user.is_authenticated():
            self.response.error_response(errno=1, errorStr="User login failed")
            return self.response.response
        login(self.request, user) 

        if do_sync:
            #sync  all syncables
            s = profile.serialize_objects()
	    if s.has_key('wizcard'):
                self.response.add_data("wizcards", s['wizcard'])
		if s.has_key('wizconnections'):
                    self.response.add_data("rolodex", s['wizconnections'])
		if s.has_key('tables'):
                    self.response.add_data("tables", s['tables'])

        return self.response.response

    def msg_has_location(self, msg_type):
        return self.sender.has_key('lat')  and self.sender.has_key('lng') and msg_type not in ['signup', 'login', 'register', 'current_location']

    def update_location(self, msg_type):
        if self.msg_has_location(msg_type):
            self.processLocationUpdate()

    def processRegister(self):
        print '{sender} at location [{locX} , {locY}] sent '.format (sender=self.sender['userID'], locX=self.sender['lat'], locY=self.sender['lng'])

        wizcard_s = None
        rolodex_s = None

        do_sync = False
        w_count = 0
        r_count = 0
        #AA:TODO: a better idiom is has_key
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

        l_userid = self.sender['userID'] 
        password = "wizard"
        #password = self.sender['password']


        #AA:TODO: refactor. get_or_create can do the same thing without having
        # to do another lookup
        try: 
            #existing user
            w_userid = self.sender['wizUserID']
            user = User.objects.get(id=w_userid)
        except:
            #create case
            user, created = User.objects.get_or_create(username=l_userid,
                                                       defaults={'first_name':first_name,
                                                                 'last_name':last_name,
                                                                 'email':email})
            do_sync = not created

            user.set_password(password)
            user.save()

        #AA: TODO: Handle auth error
        user = authenticate(username=l_userid, password=password)
        if not user.is_authenticated():
            self.response.error_response(errno=1, errorStr="User authentication failed")
            return self.response.response

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
		if s.has_key('tables'):
                    self.response.add_data("tables", s['tables'])

        #update location in ptree
        profile.create_or_update_location(self.sender['lat'], self.sender['lng'])

        self.response.add_data("wizUserID", user.pk)
        if wizcard_s:
            self.response.add_data("wizcards", wizcard_s)
        if rolodex_s:
            self.response.add_data("rolodex", rolodex_s)

        return self.response.response

    def processAddWizcard(self):
        #find user
        try:
            user = User.objects.get(id=self.sender['wizUserID'])
        except ObjectDoesNotExist:
            self.response.error_response(errno=1, errorStr="User authentication failed")
            return self.response.response

        try:
            first_name = self.sender['first_name']
        except:
            first_name = ""
        try:
            last_name = self.sender['last_name']
        except:
            last_name = ""
        try:
            phone1 = self.sender['phone1']
        except:
            phone1 = ""
        try:
            email = self.sender['email']
        except:
            email = ""
        try:
            street = self.sender['address_street1']
        except:
            street = ""
        try:
            city = self.sender['address_city']
        except:
            city = ""
        try:
            state = self.sender['address_state']
        except:
            state = ""
        try:
            country = self.sender['address_country']
        except:
            country = ""
        try:
            zipcode = self.sender['addreess_zip']
        except:
            zipcode = ""
        wizcard = Wizcard(user=user, first_name=first_name, last_name=last_name,
                          phone1=phone1, email=email, address_street1=street,
                          address_city=city, address_state=state,
                          address_country=country, address_zip=zipcode)


        #try:
        #    rawimage = self.sender['thumbnailImage']
        #    upfile = SimpleUploadedFile("%s-%s.jpg" % (wizcard.pk, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")), rawimage, "image/jpeg")
        #    wizcard.thumbnailImage.save(upfile.name, upfile) 
        #except:
        #    pass
        
        self.response.add_data("wizCardID", wizcard.pk)
        return self.response.response


    def processDeleteWizcardOwn(self):
        try:
            user = User.objects.get(id=self.sender['wizUserID'])
            wizcard1 = user.wizcard
        except ObjectDoesNotExist:
            self.response.error_response(errno=1, errorStr="Object does not exist")
            return self.response.response

        #go through all connections and uncard them
        qs = wizcard1.wizconnections.all()
        deleted_wizcards = []
        count = 0
        for wizcard2 in qs:
            Wizcard.objects.uncard(wizcard1, wizcard2)
            #Q a notif to other guy so that the app on the other side can react
            notify.send(user, recipient=wizcard2.user, 
                        verb='deleted wizcard', target=wizcard1)
            #Q a notif to sender to let him know of all wizconnections to delete
            notify.send(wizcard2.user, recipient=user,
                        verb='deleted wizcard', target=wizcard2, 
                        action_object = wizcard2)

        wizcard1.delete()
        return self.response.response

    def processDeleteWizcardRolodex(self):
        try:
            sender = User.objects.get(id=self.sender['wizUserID'])
            receiver = User.objects.get(id=self.receiver['wizUserID'])
            wizcard1 = sender.wizcard
            wizcard2 = receiver.wizcard
        except:
            self.response.error_response(errno=1, errorStr="Object does not exist")
            return self.response.response

        Wizcard.objects.uncard(wizcard1, wizcard2)
        #Q a notif to other guy so that the app on the other side can react
        notify.send(sender, recipient=receiver,
                    verb='revoked wizcard', target=wizcard1)
        return self.response.response

    def processDeleteWizcardNotification(self):
        try:
            sender = User.objects.get(id=self.sender['wizUserID'])
            receiver = User.objects.get(id=self.receiver['wizUserID'])
            wizcard1 = sender.wizcard
            wizcard2 = receiver.wizcard
        except:
            self.response.error_response(errno=1, errorStr="Object does not exist")
            return self.response.response

        #wizcard2 must have sent a wizconnection_request, lets clear it
        Wizcard.objects.wizconnection_req_clear(wizcard2, wizcard1)

        #Q a notif to other guy so that the app on the other side can react
        notify.send(sender, recipient=receiver,
                    verb='revoked wizcard', target=wizcard1)

        return self.response.response

 
    def processModifyWizcard(self):
        modify = False
        try:
            user = User.objects.get(id=self.sender['wizUserID'])
        except ObjectDoesNotExist:
            self.response.error_response(errno=1, errorStr="Object does not exist")
            return self.response.response
        try:
            wizcard = user.wizcard
        except ObjectDoesNotExist:
            #create case
            wizcard = Wizcard(user=user)
            wizcard.save()

            #this is also the time User object can get first/last name
            user.first_name = self.sender['first_name']
            user.last_name = self.sender['last_name']
            user.save()

        #AA:TODO phone1 currently should always be there 
        phone1 = self.sender['phone1']

        #check if futureUser existed for this phoneNum
        try:
            future_user = User.objects.get(username=phone1)
            if future_user.profile.is_future():
                Wizcard.objects.migrate_future_user(future_user, user)
                Notification.objects.migrate_future_user(future_user, user)
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
            rawimage = self.sender['thumbnailImage']
            upfile = SimpleUploadedFile("%s-%s.jpg" % (wizcard.pk, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")), rawimage, "image/jpeg")
            wizcard.thumbnailImage.save(upfile.name, upfile) 

        if self.sender.has_key('VideoUrl'):
            rawvideo = self.sender['VideoUrl']
            upfile = SimpleUploadedFile("%s-%s.mp4" % (wizcard.pk, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")), rawvideo, "video/mp4")
            wizcard.video.save(upfile.name, upfile) 

        if self.sender.has_key('contact_container'):
            contactContainerList = self.sender['contact_container']
            #AA: TODO: Optimize using isModified flag from app
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
        return self.response.response

    def processLocationUpdate(self):
        user = User.objects.get(id=self.sender['wizUserID'])
        profile = user.profile
        #update location in ptree
        profile.create_or_update_location(self.sender['lat'], self.sender['lng'])
        return self.response.response

    def processAcceptFlickedCard(self):
        #To Do. if app returns the connection id cookie sent by server
        #we'd just need to lookup connection from there
        try:
            sender = User.objects.get(id=self.sender['wizUserID'])
            receiver = User.objects.get(id=self.receiver['wizUserID'])
            wizcard1 = sender.wizcard
            wizcard2 = receiver.wizcard
        except:
            try:
                wizcard1 = Wizcard.objects.get(id=self.sender['wizCardID'])
                wizcard2 = Wizcard.objects.get(id=self.receiver['wizCardID'])
            except:
                self.response.error_response(errno=1, errorStr="Object does not exist")
                return self.response.response

	#create a wizconnection and then accept it
	Wizcard.objects.exchange(wizcard1, wizcard2, True)

        return self.response.response

    def processAcceptCard(self):
        #To Do. if app returns the connection id cookie sent by server
        #we'd just need to lookup connection from there
        try:
            sender = User.objects.get(id=self.sender['wizUserID'])
            receiver = User.objects.get(id=self.receiver['wizUserID'])
            wizcard1 = sender.wizcard
            wizcard2 = receiver.wizcard
        except ObjectDoesNotExist:
            self.response.error_response(errno=1, errorStr="Object does not exist")
            return self.response.response

        Wizcard.objects.accept_wizconnection(wizcard2, wizcard1)
        #Q this to the sender 
        notify.send(sender, recipient=receiver,
                    verb='accepted wizcard', target=wizcard1, 
                    action_object = wizcard2)

        return self.response.response

    def processGetNotifications(self):
        #AA: TODO: Change this to get userId from session
        try:
            user = User.objects.get(id=self.sender['wizUserID'])
        except ObjectDoesNotExist:
            self.response.error_response(errno=1, errorStr="Object does not exist")
            return self.response.response

        #AA: TODO: Check if this is sorted by time
        notifications = Notification.objects.unread(user)
        notifResponse = NotifResponse(notifications)

        #any wizcards dropped nearby
        try:
            lat = self.sender['lat']
            lng = self.sender['lng']
        except:
            try:
                lat = user.profile.get_location().lat
                lng = user.profile.get_location().lng
            except:
                #maybe location timedout. Shouldn't happen if messages from app
                #are coming correctly...
                return notifResponse.response

        #AA:TODO: Use come caching framework to cache these
        #comment for now. ios app crashes since the new notifs are i
        #not yet handled
        flicked_wizcards, count = WizcardFlick.objects.lookup(lat, lng, 3)
        if count:
            notifResponse.notifFlickedWizcardLookup(count, flicked_wizcards)

        users, count = user.profile.lookup(3)
        if count:
            notifResponse.notifUserLookup(count, users)

        #tables is a smaller entity...get the tables as well instead of just count
        tables, count = VirtualTable.objects.lookup(lat, lng, 3)
        if count:
            notifResponse.notifTableLookup(count, tables)

        Notification.objects.mark_all_as_read(user)
        return notifResponse.response

    def processSendCardToContacts(self):
        #implicitly create a bidir cardship (since this is from contacts)
        #and also Q the other guys cards here
        count = 0
        try:
            sender = User.objects.get(id=self.sender['wizUserID'])
            wizcard1 = sender.wizcard
        except ObjectDoesNotExist:
            self.response.error_response(errno=1, errorStr="Object does not exist")
            return self.response.response

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
                        return self.processSendCardToFutureContacts(phones, wizcard1)

            except:
                #AA:TODO: what to do ?
                self.response.error_response(errno=2, errorStr="something's not right")

        self.response.add_data("count", count)
        return self.response.response


    def processVerifyContacts(self):
        return self.response.response

    def processSendCardToFutureContacts(self, phones, wizcard):
        for phone in phones:
            username = wizlib.convert_phone(phone)
            #create a dummy user using the phone number as userID
            try:
                #TODO: handle multiple phones or restrict app to send one
                user, created = User.objects.get_or_create(username=username)
                if created:
                    Wizcard(user=user).save()
                    user.profile.set_future()
                else:
                    assert user.profile.is_future(), 'not a future user'

                err = Wizcard.objects.exchange(wizcard, user.wizcard, False)
                if err['Error'] != "OK":
                    self.response.error_response(errno=err['Error'], 
                                                 errorStr=err['Description'])
            except:
                pass
        return self.response.response

    def processSendCardUC(self):
        try:
            sender = User.objects.get(id=self.sender['wizUserID'])
            receivers = self.receiver['wizUserIDs']
            wizcard1 = sender.wizcard
        except ObjectDoesNotExist:
            self.response.error_response(errno=1, errorStr="Object does not exist")
            return self.response.response

        for receiver in receivers:
            try:
                wizcard2 = User.objects.get(id=receiver).wizcard
                err = Wizcard.objects.exchange(wizcard1, wizcard2, False)
                if err['Error']:
                    self.response.error_response(errno=err['Error'], 
                                                 errorStr=err['Description'])
            except:
                self.response.error_response(errno=1, errorStr="something went wrong")

        return self.response.response

    def processQueryUserByLocation(self):
        user = User.objects.get(id=self.sender['wizUserID'])
        profile = user.profile
        #update location in ptree
        profile.create_or_update_location(self.sender['lat'], 
                                          self.sender['lng'])
        lookup_result, count = profile.lookup(3)
        if count:
            users_s = UserProfile.objects.serialize(lookup_result)
            self.response.add_data("queryResult", users_s)
            self.response.add_data("count", count)
        else:
            self.response.error_response(errno=1, errorStr="Query returned no results")

        return self.response.response

    def processQueryUserByName(self):
        excludeUserID = self.sender['wizUserID']

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

        result, count = Wizcard.objects.find_users(excludeUserID, name, phone, email)
        #send back to app for selection

        if (count):
            users = serialize(result, **fields.wizcard_user_query_template)
            self.response.add_data("queryResult", users)
            self.response.add_data("count", count)
        else:
            self.response.error_response(errno=1, errorStr="Query returned no results")
 
        return self.response.response

    def processQueryTable(self):
        if self.sender.has_key('lat') and self.sender.has_key('lng'):
            lat = self.sender['lat']
            lng = self.sender['lng']
            self.processQueryTableByLocation(lat, lng)
        elif self.sender.has_key('table_name'):
            name = self.sender['table_name']
            self.processQueryTableByName(name)
        else:
            self.response.error_response(errno=1, errorStr="invalid table detail")


        return self.response.response


    def processQueryTableByName(self, name):
        try:
            tables = VirtualTable.objects.filter(Q(tablename__icontains=name))
        except ObjectDoesNotExist:
            self.response.error_response(errno=1, errorStr="Object does not exist")
            return self.response.response
        count = tables.count()

        if count:
            tables_s = VirtualTable.objects.serialize(tables)
            self.response.add_data("queryResult", tables_s)
            self.response.add_data("count", count)
            
        return self.response.response

    def processQueryTableByLocation(self, lat, lng):
        tables, count = VirtualTable.objects.lookup(lat=lat, lng=lng, n=3)
        if count:
            tables_s = VirtualTable.objects.serialize(tables)
            self.response.add_data("queryResult", tables_s)
            self.response.add_data("count", count)
        else:
            self.response.error_response(errno=1, errorStr="Query returned no results")

        return self.response.response

    def processGetTableDetails(self):
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

        return self.response.response

    DEFAULT_FLICK_TIMEOUT = 10
    def processWizcardFlick(self):
        try:
            user = User.objects.get(id=self.sender['wizUserID'])
        except ObjectDoesNotExist:
            self.response.error_response(errno=1, errorStr="Object does not exist")
            return self.response.response
        try:
            wizcard = user.wizcard
        except:
            self.response.error_response(errno=1, errorStr="Object does not exist")
            return self.response.response
        try:
            flick_timeout = self.sender['flickTimeout']
        except:
            flick_timeout = self.DEFAULT_FLICK_TIMEOUT

        #AA:TODO: Check implications of LocationMgr object deletion when timeout happens
        lat = user.profile.get_location().lat
        lng = user.profile.get_location().lng
        
	flick_card = WizcardFlick.objects.check_location(lat, lng)

	if flick_card:
	    flick_card.location.reset_timer()
        else:
	    flick_card = WizcardFlick.objects.create(wizcard=wizcard, lat=lat, lng=lng)
            location = flick_card.create_location(lat, lng)
            location.start_timer(flick_timeout)

        self.response.add_data("flickCardID", flick_card.pk)
        return self.response.response

    def processCreateTable(self):
        try:
            user = User.objects.get(id=self.sender['wizUserID'])
        except ObjectDoesNotExist:
            self.response.error_response(errno=1, errorStr="Object does not exist")
            return self.response.response

        tablename = self.sender['table_name']
        lat = self.sender['lat']
        lng = self.sender['lng']
        secure = self.sender['secureTable']
        lifetime = self.sender['lifetime']
        if not lifetime:
            lifetime = 30
        if secure:
            password = self.sender['password']
        else:
            password = ""
        table = VirtualTable.objects.create(tablename=tablename, secureTable=secure, 
                                            password=password, creator=user, 
                                            life_time=lifetime)
        #update location in ptree
        #AA:TODO move create to overridden create in VirtualTable
        table.create_location(lat, lng)
        l = table.get_location()
	l.start_timer(lifetime)
        table.join_table_and_exchange(user, password, False)
        table.save()
        self.response.add_data("tableID", table.pk)
        return self.response.response

    def processJoinTable(self):
        try:
            user = User.objects.get(id=self.sender['wizUserID'])
            table = VirtualTable.objects.get(id=self.sender['tableID'])
        except ObjectDoesNotExist:
            self.response.error_response(errno=1, errorStr="Object does not exist")
            return self.response.response

        if user is table.creator:
            self.response.error_response(errno=1, errorStr="Already joined table")
            return self.response.response

        if table.isSecure():
            password = self.sender['password']
        else:
            password = ""
        
        joined = table.join_table_and_exchange(user, password, True)

        if joined is None:
            self.response.error_response(errno=1, errorStr="Invalid Password")
        else:
            self.response.add_data("tableID", joined.pk)
        return self.response.response

    def processLeaveTable(self):
        try:
            user = User.objects.get(id=self.sender['wizUserID'])
        except ObjectDoesNotExist:
            self.response.error_response(errno=1, errorStr="Object does not exist")
            return self.response.response
        try:
            table = VirtualTable.objects.get(id=self.sender['tableID'])
            leave = table.leave_table(user)
            self.response.add_data("tableID", leave.pk)
        except:
            pass
        return self.response.response

    def processDestroyTable(self):
        try:
            user = User.objects.get(id=self.sender['wizUserID'])
            table = VirtualTable.objects.get(id=self.sender['tableID'])
        except ObjectDoesNotExist:
            self.response.error_response(errno=1, errorStr="Object does not exist")
            return self.response.response

        if table.creator == user:
            table.delete()
        else:
            self.response.error_response(errno=1, errorStr="User is not the creator")
        return self.response.response


wizrequest_handler = WizRequestHandler.as_view()
#wizconnection_request = login_required(WizConnectionRequestView.as_view())

