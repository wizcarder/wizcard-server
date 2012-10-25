"""
.. autofunction:: wizconnection_request

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
import operator
from django.http import HttpResponse
from django.http import HttpResponseBadRequest, Http404
from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core import serializers
from wizcardship.models import WizConnectionRequest, Wizcard
from notifications.models import notify, Notification
from json_wrapper import DataDumper
from response import Response, NotifResponse
import msg_test

logger = logging.getLogger(__name__)

class WizRequestHandler(View):

    def get(self, request, *args, **kwargs):
        message = msg_test.get_cards1
        #msg = json.loads(message)

        # process request
        ret = self.processIncomingMessage(message)
        #send response
        logger.debug('sending response')
        return HttpResponse(json.dumps(ret))

    def test(self, request):
        return HttpResponse("ok")

    def post(self, request, *args, **kwargs):
        self.request = request
        msg = json.loads(request.body)

        logger.debug('Received POST request, msgType: %s', msg['msgType'])

        # Dispatch to appropriate message handler
        ret = self.processIncomingMessage(msg)
        #send response
        return HttpResponse(json.dumps(ret))

    def processIncomingMessage(self, message):
        self.response = Response()
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
            'send_query_user'           : self.processQueryUser
        }

        # Dispatch to appropriate message handler
        return msgHandlers[message['msgType']](message)

    def processRegister(self, message):

        logger.debug("")
        try:
            firstname = message['firstname']
        except:
            firstname = ""

        try:
            lastname = message['lastname']
        except:
            lastname = ""

        try:
            email = message['email']
        except:
            email = ""

        l_userid = message['userID'] 
        password = "wizard"

        try: 
            #existing user
            w_userid = message['wizUserID']
            user = User.objects.get(id=w_userid)
        except:
            #create case
            #AA:TODO: ideally just create should be here. Did this to get around
            # a bug in the app for now
            user, created = User.objects.get_or_create(username=l_userid,
                                                       defaults={'first_name':firstname,
                                                                 'last_name':lastname,
                                                                 'email':email})
            
            user.set_password(password)
            user.save()

        user = authenticate(username=l_userid, password=password)

        if user is not None and user.is_active:
            # Correct password, and the user is marked "active"
            login(self.request, user)
            self.response.add_data("wizUserID", user.id)
        else:
            self.response.add_result("Error", 1)
            self.response.add_result("Description", "User authentication failed")

        return self.response.response

    def processDeleteWizcardOwn(self, message):
        return self.response.response

    def processDeleteWizcardRolodex(self, message):
        return self.response.response

    def processDeleteWizcardNotification(self, message):
        body = message['message']
        user = User.objects.get(id=message['wizUserID'])
        #TODO: AA: change this to handle multple wizcards
        wizcard1 = user.wizcards.all()[0]
        #wizcard1 = get_object_or_404(Wizcard, id=message['wizCardID'])
        wizcard2 = get_object_or_404(Wizcard, id=body['wizCardID'])
        Wizcard.objects.uncard(wizcard1, wizcard2)
        #Q a notif to other guy so that the app on the other side can react
        notify.send(wizcard1.user, recipient=wizcard2.user,
                    verb='revoked wizcard', target=wizcard1)
        return self.response.response

    def processAddWizcard(self, message):
        #find user
        body = message['message']

        try:
            #user = get_object_or_404(User, id=message['wizUserID'])
            user = User.objects.get(id=message['wizUserID'])
        except:
            user = User.objects.get(username=message['userID'])

        try:
            company = body['company']
        except:
            company = ""

        try:
            title = body['title']
        except:
            title = ""
        try:
            phone1 = body['phone']
        except:
            phone1 = ""
        try:
            email = body['email']
        except:
            email = ""
        try:
            street = body['street']
        except:
            street = ""
        try:
            city = body['city']
        except:
            city = ""
        try:
            state = body['state']
        except:
            state = ""
        try:
            country = body['country']
        except:
            country = ""
        try:
            zipcode = body['zip']
        except:
            zipcode = ""

        wizcard = Wizcard(user=user, company=company,
                          title=title, phone1=phone1,
                          email=email, address_street1=street,
                          address_city=city, address_state=state,
                          address_country=country, address_zip=zipcode)
        wizcard.save()
        
        self.response.add_data("wizCardID", wizcard.id)
        return self.response.response


    def processModifyWizcard(self, message):
        body = message['message']
        #find card
        wizcard = get_object_or_404(Wizcard, id=body['wizCardID'])

        try:
            company = body['company']
            wizcard.company = company
        except:
            company = ""
        try:
            title = body['title']
            wizcard.title = title
        except:
            title = ""
        try:
            phone1 = body['phone']
            wizcard.phone1 = phone1
        except:
            phone1 = ""
        try:
            phone2 = body['phone']
            wizcard.phone2 = phone2
        except:
            phone2 = ""
        try:
            email = body['email']
            wizcard.email = email
        except:
            email = ""
        try:
            street1 = body['address_street1']
            wizcard.street1 = street1
        except:
            street1 = ""
        try:
            city = body['address_city']
            wizcard.city = city
        except:
            city = ""
        try:
            state = body['address_state']
            wizcard.state = state
        except:
            state = ""
        try:
            country = body['address_country']
            wizcard.country = country
        except:
            country = ""
        try:
            zipcode = body['address_zip']
            wizcard.zipcode = zipcode
        except:
            zipcode = ""

        wizcard.save()

        self.response.add_data("wizCardID", wizcard.id)
        return self.response.response

    def processLocationUpdate(self, message):
        response = "location update"
        return response

    def processAcceptCard(self, message):
        #To Do. if app returns the connection id cookie sent by server
        #we'd just need to lookup connection from there
        body = message['message']
        user = User.objects.get(id=message['wizUserID'])
        wizcard1 = user.wizcards.all()[0]
        wizcard2 = Wizcard.objects.get(id=body['wizCardID'])
        accept_wizconnection(wizcard2, wizcard1)
        #Q this to the sender 
        notify.send(user, recipient=wizcard2.user,
                    verb='accepted wizcard', target=wizcard1)

        return self.response.response

    def processGetNotifications(self, message):
        #AA: TODO: Change this to get userId from session
        
        try:
            #user = get_object_or_404(User, id=message['wizUserID'])
            user = get_object_or_404(User, id=message['wizUserID'])
        except:
            user = User.objects.get(username=message['userID'])

        #AA: TODO: Check if this is sorted by time
        notifications = Notification.objects.unread(user)

        notifResponse = NotifResponse()

        notifHandler = {
            'wizconnection request untrusted' : notifResponse.notifWizConnectionU,
            'wizconnection request trusted'   : notifResponse.notifWizConnectionT,
            'accepted wizcard'      : notifResponse.notifAcceptedWizcard,
            'revoked wizcard'       : notifResponse.notifRevokedWizcard
        }

        for notification in notifications:
            notifHandler[notification.verb](notification)

        Notification.objects.mark_all_as_read(user)
        return notifResponse.response



    def processSendCardToContacts(self, message):
        #implicitly create a bidir cardship (since this is from contacts)
        #and also Q the other guys cards here
        count = 0
        body = message['message']
        wizcard1 = Wizcard.objects.get(id=body['wizCardID'])
        user = wizcard1.user
        recipients = body['contacts']
        for recipient in recipients:
            try:
                emails = recipient['emailAddresses']
                for email in emails:
                    target_user, query_count = find_users(name=None, phone=None, email=email)
                    #AA:TODO: Fix for multiple wizcards. Get it by default flag
                    assert query_count == 1
                    if query_count:
                        #AA:TODO: [0] is no good. Also handle the case where 
                        # target_user doesn't have any wizcards
                        wizcard2 = target_user[0].wizcards.all()[0]
                        #create bidir cardship
                        if Wizcard.objects.are_wizconnections(wizcard1, wizcard2):
                            self.response.add_result("Error", 2)
                            self.response.add_result("Description", "already connected to user")
                        else:
                            count += 1
                            Wizcard.objects.becard(wizcard1, wizcard2) 
                            Wizcard.objects.becard(wizcard2, wizcard1) 
                            #Q this to the receiver and vice-versa
                            notify.send(user, recipient=target_user[0], 
                                        verb='wizconnection request trusted', target=wizcard1)
                            notify.send(target_user[0], recipient=user,
                                        verb='wizconnection request trusted', target=wizcard2)
            except:
                #AA:TODO: what to do ?
                self.response.add_result("Error", 2)
                self.response.add_result("Description", "something's not right")

        self.response.add_data("count", count)
        return self.response.response

    def processSendCardUC(self, message):
        body = message['message']
        wizcard1 = Wizcard.objects.get(id=body['wizCardID'])
        recipient = body['wizUserID']
        try:
            try:
                source_user = User.objects.get(id = message['wizUserID'])
            except:
                source_user = User.objects.get(username = message['userID'])
            target_user = User.objects.get(id=recipient)
            #AA: TODO: Extend to support multiple wizcards per user
            ##AA: TODO: What if the recipient has no wizcard ?
            wizcard2 = target_user.wizcards.all()[0]

            #create bidir cardship
            if Wizcard.objects.are_wizconnections(wizcard1, wizcard2):
                self.response.add_result("Error", 2)
                self.response.add_result("Description", "Already connected to user")
            else:
                #send a connection request
                try:
                    # If there's a wizconnection request from the other user accept it.
                    accept_wizconnection(wizcard1, wizcard2)
                except Http404:
                    # If we already have an active wizconnection request IntegrityError
                    # will be raised and the transaction will be rolled back.
                    wizconnection = WizConnectionRequest.objects.create(
                        from_wizcard=wizcard1,
                        to_wizcard=wizcard2,
                        message="wizconnection request")

                    #Q this to the receiver
                    notify.send(source_user, recipient=target_user, 
                                verb='wizconnection request untrusted', target=wizcard1)
        except:
            #AA:TODO: what to do ?
            self.response.add_result("Error", 1)
            self.response.add_result("Description", "something's not right")

        return self.response.response


    #AA: This can be the same message as above. Treat it separately for now
    def processQueryUser(self, message):
        body = message['message']
        try:
            name = body['name']
        except:
            name = None
        try:
            phone = body['phone']
        except:
            phone = None
        try:
            email = body['email']
        except:
            email = None

        recipients, count = find_users(name, phone, email)
        #send back to app for selection

        if (count):
            response_fields = ["id", "username", "first_name", "last_name"]
            dumper = DataDumper()
            dumper.selectObjectFields('User', response_fields)
            users = dumper.dump(recipients, 'json')
            self.response.add_data("queryResult", users)
            self.response.add_data("count", count)
        else:
            self.response.add_result("Error", 1)
            self.response.add_result("Description", "Query returned no results")

        return self.response.response

def find_users(name, phone, email):
    #name can be first name, last name or even combined
    #any of the arguments may be null

    qlist = []

    if name != None:
        split = name.split()
        for n in split:
            name_result = (Q(first_name__icontains=n) | Q(last_name__icontains=n))
            qlist.append(name_result)

    #AA:TODO: Phone is not present in the django user (among other fields).
    # needs user profile addition
    #phone
    #if phone != None:
    #    phone_result = (Q(phone1__contains=phone) | Q(phone2__contains=phone))
    #    qlist.append(phone_result)

    #email
    if email != None:
        email_result = Q(email=email)
        qlist.append(email_result)

    #not sure at this point whether it should be OR or AND
    result = User.objects.filter(reduce(operator.or_, qlist))

    return result, result.count()

def accept_wizconnection(from_wizcard, to_wizcard):
    get_object_or_404(WizConnectionRequest, from_wizcard=from_wizcard,
                      to_wizcard=to_wizcard).accept()



wizrequest_handler = WizRequestHandler.as_view()
#wizconnection_request = login_required(WizConnectionRequestView.as_view())
