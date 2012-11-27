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
from django.http import HttpResponseBadRequest, Http404
from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core import serializers
from wizcardship.models import WizConnectionRequest, Wizcard
from notifications.models import notify, Notification
from virtual_table.models import VirtualTable
from json_wrapper import DataDumper
from response import Response, NotifResponse
from wizserver import wizlib
import wizlib
import msg_test, fields


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
        print ret
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

        #print '{sender} sent "{type}"'.format (sender=self.sender['userID'], type=self.header['msgType'])

        #print '{sender} at location [{locX} , {locY}] sent "{type}"'.format (sender=self.sender['userID'], locX=self.sender['lat'], locY=self.sender['lng'], type=self.header['msgType'])

        self.response = Response()



    def processIncomingMessage(self):
        msgHandlers = {
            'register'                  : self.processRegister,
            'add_card'                  : self.processAddWizcard,
            'edit_card'                 : self.processModifyWizcard,
            'delete_card'               : self.processDeleteWizcardOwn,
            'delete_notification_card'  : self.processDeleteWizcardNotification,
            'delete_rolodex_card'       : self.processDeleteWizcardRolodex,
            'update'                    : self.processLocationUpdate,
            'add_notification_card'     : self.processAcceptCard,
            'get_cards'                 : self.processGetNotifications,
            'send_card_to_contacts'     : self.processSendCardToContacts,
            'send_card_to_user'         : self.processSendCardUC,
            'send_query_user'           : self.processQueryUser,
            'show_table_list'           : self.processQueryTable,
            'table_details'             : self.processGetTableDetails,
            'create_table'              : self.processCreateTable,
            'join_table'                : self.processJoinTable,
            'leave_table'               : self.processLeaveTable,
            'destroy_table'             : self.processDestroyTable
        }

        # Dispatch to appropriate message handler
        return msgHandlers[self.msgType]()

    def processRegister(self):
        print '{sender} at location [{locX} , {locY}] sent '.format (sender=self.sender['userID'], locX=self.sender['lat'], locY=self.sender['lng'])

        do_sync = False
        w_count = 0
        r_count = 0
        try:
            firstname = self.sender['firstname']
        except:
            firstname = ""

        try:
            lastname = self.sender['lastname']
        except:
            lastname = ""

        try:
            email = self.sender['email']
        except:
            email = ""

        l_userid = self.sender['userID'] 
        password = "wizard"

        try: 
            #existing user
            w_userid = self.sender['wizUserID']
            user = User.objects.get(id=w_userid)
        except:
            #create case
            #AA:TODO: ideally just create should be here. Did this to get around
            # a bug in the app for now
            do_sync = True
            user, created = User.objects.get_or_create(username=l_userid,
                                                       defaults={'first_name':firstname,
                                                                 'last_name':lastname,
                                                                 'email':email})
            user.set_password(password)
            user.save()

        user = authenticate(username=l_userid, password=password)

        if do_sync == True:
            #sync the app from server
            wizcards = []
            rolodex = []
            notifications = []
            #sync own card
            for wizcard in user.wizcards.all():
                w_count += 1
                wizcards.append(wizcard)
                #add connected wizcards in order
                if wizcard.wizconnection_count():
                    rolodex.extend(wizcard.wizconnections.all())
                    r_count += 1

            if w_count:
                dumper = DataDumper()
                response_fields = fields.fields['wizcard_fields']
                dumper.selectObjectFields('Wizcard', response_fields)
                wizcards_out = dumper.dump(wizcards, 'json')

            if r_count:
                dumper = DataDumper()
                response_fields = fields.fields['wizcard_fields']
                dumper.selectObjectFields('Wizcard', response_fields)
                rolodex_out = dumper.dump(rolodex, 'json')

                #AA:TODO: Ugly. Find a better way to add arbitrary data into json
                # via json_wrapper
                # for now, walking the rolodex 2d array and adding the self wizCardID
                for i in range(r_count):
                    rolodex_out[i]['wizCardID'] = wizcards[i].pk

                #prune out empty elements
                rolodex_out = filter(lambda a:len(a) != 0, rolodex_out)

        if user is not None and user.is_active:
            # Correct password, and the user is marked "active"
            login(self.request, user)
            self.response.add_data("wizUserID", user.pk)
            if w_count != 0:
                self.response.add_data("wizcards", wizcards_out)
            if r_count != 0:
                self.response.add_data("rolodex", rolodex_out)
                
        else:
            self.response.add_result("Error", 1)
            self.response.add_result("Description", "User authentication failed")

        return self.response.response

    def processAddWizcard(self):
        #find user
        user = User.objects.get(id=self.sender['wizUserID'])

        try:
            first_name = self.sender['first']
        except:
            first_name = ""
        try:
            last_name = self.sender['last']
        except:
            last_name = ""
        try:
            company = self.sender['company']
        except:
            company = ""
        try:
            title = self.sender['title']
        except:
            title = ""
        try:
            phone1 = self.sender['phone']
        except:
            phone1 = ""
        try:
            email = self.sender['email']
        except:
            email = ""
        try:
            street = self.sender['street']
        except:
            street = ""
        try:
            city = self.sender['city']
        except:
            city = ""
        try:
            state = self.sender['state']
        except:
            state = ""
        try:
            country = self.sender['country']
        except:
            country = ""
        try:
            zipcode = self.sender['zip']
        except:
            zipcode = ""

        wizcard = Wizcard(user=user, first_name=first_name, last_name=last_name,
                          company=company,
                          title=title, phone1=phone1,
                          email=email, address_street1=street,
                          address_city=city, address_state=state,
                          address_country=country, address_zip=zipcode)
        wizcard.save()
        
        self.response.add_data("wizCardID", wizcard.pk)
        return self.response.response


    def processDeleteWizcardOwn(self):
        user = User.objects.get(id=self.sender['wizUserID'])
        wizcard1 = get_object_or_404(Wizcard, id=self.sender['wizCardID'])

        #go through all connections and uncard them
        qs = wizcard1.wizconnections.all()
        deleted_wizcards = []
        count = 0
        for wizcard2 in qs:
            Wizcard.objects.uncard(wizcard1, wizcard2)
            #Q a notif to other guy so that the app on the other side can react
            notify.send(wizcard1.user, recipient=wizcard2.user, 
                        verb='deleted wizcard', target=wizcard1)
            #Q a notif to sender to let him know of all wizconnections to delete
            notify.send(wizcard2.user, recipient=user,
                        verb='deleted wizcard', target=wizcard2, 
                        action_object = wizcard2)

        wizcard1.delete()
        return self.response.response

    def processDeleteWizcardRolodex(self):
        user = User.objects.get(id=self.sender['wizUserID'])
        #TODO: AA: change this to handle multple wizcards
        wizcard1 = get_object_or_404(Wizcard, id=self.sender['wizCardID'])
        wizcard2 = get_object_or_404(Wizcard, id=self.receiver['wizCardID'])
        Wizcard.objects.uncard(wizcard1, wizcard2)
        #Q a notif to other guy so that the app on the other side can react
        notify.send(wizcard1.user, recipient=wizcard2.user,
                    verb='revoked wizcard', target=wizcard1)
        return self.response.response

    def processDeleteWizcardNotification(self):
        user = User.objects.get(id=self.sender['wizUserID'])
        wizcard1 = get_object_or_404(Wizcard, id=self.sender['wizCardID'])
        wizcard2 = get_object_or_404(Wizcard, id=self.receiver['wizCardID'])

        #wizcard2 must have sent a wizconnection_request, lets clear it
        Wizcard.objects.wizconnection_req_clear(wizcard2, wizcard1)

        #Q a notif to other guy so that the app on the other side can react
        notify.send(wizcard1.user, recipient=wizcard2.user,
                    verb='revoked wizcard', target=wizcard1)
        return self.response.response

 
    def processModifyWizcard(self):
        #find card
        wizcard = get_object_or_404(Wizcard, id=self.sender['wizCardID'])

        try:
            first_name = self.sender['first']
            wizcard.first_name = first_name
        except:
            first_name = ""
        try:
            last_name = self.sender['last']
            wizcard.last_name = last_name
        except:
            last_name = ""
        try:
            company = self.sender['company']
            wizcard.company = company
        except:
            company = ""
        try:
            title = self.sender['title']
            wizcard.title = title
        except:
            title = ""
        try:
            phone1 = self.sender['phone']
            wizcard.phone1 = phone1
        except:
            phone1 = ""
        try:
            phone2 = self.sender['phone']
            wizcard.phone2 = phone2
        except:
            phone2 = ""
        try:
            email = self.sender['email']
            wizcard.email = email
        except:
            email = ""
        try:
            street1 = self.sender['address_street1']
            wizcard.street1 = street1
        except:
            street1 = ""
        try:
            city = self.sender['address_city']
            wizcard.city = city
        except:
            city = ""
        try:
            state = self.sender['address_state']
            wizcard.state = state
        except:
            state = ""
        try:
            country = self.sender['address_country']
            wizcard.country = country
        except:
            country = ""
        try:
            zipcode = self.sender['address_zip']
            wizcard.zipcode = zipcode
        except:
            zipcode = ""

        wizcard.save()

        self.response.add_data("wizCardID", wizcard.pk)
        return self.response.response

    def processLocationUpdate(self):
        response = "location update"
        return response

    def processAcceptCard(self):
        #To Do. if app returns the connection id cookie sent by server
        #we'd just need to lookup connection from there
        user = User.objects.get(id=self.sender['wizUserID'])
        wizcard1 = user.wizcards.all()[0]
        #wizcard1 = Wizcard.objects.get(id=self.receiver['wizCardID'])
        wizcard2 = Wizcard.objects.get(id=self.receiver['wizCardID'])
        wizlib.accept_wizconnection(wizcard2, wizcard1)
        #Q this to the sender 
        notify.send(user, recipient=wizcard2.user,
                    verb='accepted wizcard', target=wizcard1, 
                    action_object = wizcard2)

        return self.response.response

    def processGetNotifications(self):
        #AA: TODO: Change this to get userId from session

        user = get_object_or_404(User, id=self.sender['wizUserID'])

        #AA: TODO: Check if this is sorted by time
        notifications = Notification.objects.unread(user)

        notifResponse = NotifResponse()

        notifHandler = {
            'wizconnection request untrusted' : notifResponse.notifWizConnectionU,
            'wizconnection request trusted'   : notifResponse.notifWizConnectionT,
            'accepted wizcard'      : notifResponse.notifAcceptedWizcard,
            'revoked wizcard'       : notifResponse.notifRevokedWizcard,
            'deleted wizcard'       : notifResponse.notifRevokedWizcard,
            'destroy table'         : notifResponse.notifDestroyedTable
        }

        for notification in notifications:
            notifHandler[notification.verb](notification)

        Notification.objects.mark_all_as_read(user)
        return notifResponse.response



    def processSendCardToContacts(self):
        #implicitly create a bidir cardship (since this is from contacts)
        #and also Q the other guys cards here
        count = 0
        source_user = User.objects.get(id = self.sender['wizUserID'])
        wizcard1 = Wizcard.objects.get(id=self.sender['wizCardID'])
        #A:TODO: Cross verify user agains wizcard
        recipients = self.receiver['contacts']
        for recipient in recipients:
            try:
                emails = recipient['emailAddresses']
                for email in emails:
                    target_wizcards, query_count = wizlib.find_users(source_user.pk, name=None, phone=None, email=email)
                    #AA:TODO: Fix for multiple wizcards. Get it by default flag
                    if query_count:
                        for wizcard2 in target_wizcards:
                            #create bidir cardship
                            if not Wizcard.objects.are_wizconnections(wizcard1, wizcard2):
                                err = wizlib.exchange(wizcard1, wizcard2, True)
                                exchange_implicit(wizcard1, wizcard2)
                                count += 1
            except:
                #AA:TODO: what to do ?
                self.response.add_result("Error", 2)
                self.response.add_result("Description", "something's not right")

        self.response.add_data("count", count)
        return self.response.response

    def processSendCardUC(self):
        try:
            wizcard1 = Wizcard.objects.get(id=self.sender['wizCardID'])
            #AA: TODO: Extend to support multiple wizcards per user
            ##AA: TODO: What if the recipient has no wizcard ?
            wizcard2 = Wizcard.objects.get(id=self.receiver['wizCardID'])
            source_user = wizcard1.user
            target_user = wizcard2.user

            err = wizlib.exchange(wizcard1, wizcard2, False)
            self.response.add_result("Error", err['Error'])
            self.response.add_result("Description". err['Description'])

        except:
            #AA:TODO: what to do ?
            self.response.add_result("Error", 1)
            self.response.add_result("Description", "something's not right")

        return self.response.response


    #AA: This can be the same message as above. Treat it separately for now
    def processQueryUser(self):
        userID = self.sender['wizUserID']
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

        result, count = wizlib.find_users(userID, name, phone, email)
        #send back to app for selection

        if (count):
            response_fields = fields.fields['query_fields']
            dumper = DataDumper()
            dumper.selectObjectFields('Wizcard', response_fields)
            users = dumper.dump(result, 'json')
            self.response.add_data("queryResult", users)
            self.response.add_data("count", count)
        else:
            self.response.add_result("Error", 1)
            self.response.add_result("Description", "Query returned no results")
 
        print "returning processQueryResponse"
        print self.response.response

        return self.response.response

    def processQueryTable(self):
        try:
            lat = self.sender['lat']
            lng = self.sender['lng']
            self.processQueryTableByLocation(lat, lng)
        except:
            name = self.sender['table_name']
            self.processQueryTableByName(name)

        return self.response.response


    def processQueryTableByName(self, name):
        tables = VirtualTable.objects.filter(Q(tablename__icontains=name))
        count = tables.count()

        if count:
            response_fields = fields.fields['table_fields']
            dumper = DataDumper()
            dumper.selectObjectFields('VirtualTable', response_fields)
            tables = dumper.dump(tables, 'json')
            self.response.add_data("queryResult", tables)
            self.response.add_data("count", count)
            

        return self.response.response

    def processQueryTableByLocation(self, lat, lng):
        result, count = VirtualTable.objects.get_closest_n(3, lat, lng)
        if count:
            response_fields = fields.fields['table_fields']
            dumper = DataDumper()
            dumper.selectObjectFields('VirtualTable', response_fields)
            tables = dumper.dump(result, 'json')
            self.response.add_data("queryResult", tables)
            self.response.add_data("count", count)
        else:
            self.response.add_result("Error", 1)
            self.response.add_result("Description", "Query returned no results")

        return self.response.response

    def processGetTableDetails(self):
        table_id = self.sender['tableID']
        #get the members
        membership = VirtualTable.objects.get(id=table_id)
        count = membership.count()
        if count:
            members = map(lambda m: (User.objects.get(id=m.user_id).first_name, 
                                     User.objects.get(id=m.user_id).last_name),
                          membership)
            self.response.add_result("Members", members)
            self.response.add_result("Count", count)
        return self.response.response


    def processCreateTable(self):
        user = User.objects.get(id=self.sender['wizUserID'])
        tablename = self.sender['table_name']
        lat = self.sender['lat']
        lng = self.sender['lng']
        secure = self.sender['isSecure']
        if secure == 1:
            password = self.sender['password']
        else:
            password = ""
        table = VirtualTable.objects.create(tablename=tablename, lat=lat, lng=lng,
                                           isSecure=secure, password=password,
                                           creator=user)

        table.join_table_and_exchange(user, password, False)
        table.save()
        self.response.add_data("tableID", table.pk)
        return self.response.response

    def processJoinTable(self):
        user = User.objects.get(id=self.sender['wizUserID'])
        table = VirtualTable.objects.get(id=self.sender['tableID'])
        if table.isSecure:
            password = self.sender['password']
        else:
            password = ""
        
        joined = table.join_table_and_exchange(user, password, True)

        if joined is None:
            self.response.add_result("Error", 1)
            self.response.add_result("Description", "Invalid Password")
        else:
            self.response.add_data("tableID", joined.pk)
        return self.response.response

    def processLeaveTable(self):
        user = User.objects.get(id=self.sender['wizUserID'])
        try:
            table = VirtualTable.objects.get(id=self.sender['tableID'])
            leave = table.leave_table(user)
            self.response.add_data("tableID", leave.pk)
        except:
            pass
        return self.response.response

    def processDestroyTable(self):
        user = User.objects.get(id=self.sender['wizUserID'])
        table = VirtualTable.objects.get(id=self.sender['tableID'])
        #we need to notify all members of deletion
        members = table.users.all()

        if table.creator == user:
            for member in members:
                notify.send(user, recipient=member, verb='destroy table', target=table)
            table.delete_table(user)
        else:
            self.response.add_result("Error", 1)
            self.response.add_result("Description", "User is not the creator")
        return self.response.response


wizrequest_handler = WizRequestHandler.as_view()
#wizconnection_request = login_required(WizConnectionRequestView.as_view())

