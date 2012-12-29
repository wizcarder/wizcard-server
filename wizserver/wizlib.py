import pdb
import operator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest, Http404
import geohash
#AA:TODO remove *
from wizcardship.models import *
from notifications.models import notify, Notification

def accept_wizconnection(from_wizcard, to_wizcard):
    get_object_or_404(WizConnectionRequest, from_wizcard=from_wizcard,
                      to_wizcard=to_wizcard).accept()


def exchange_implicit(wizcard1, wizcard2):
    source_user = wizcard1.user
    target_user = wizcard2.user

    Wizcard.objects.becard(wizcard1, wizcard2) 
    Wizcard.objects.becard(wizcard2, wizcard1) 
    #Q this to the receiver and vice-versa
    notify.send(source_user, recipient=wizcard2.user,
                verb='wizconnection request trusted', 
                target=wizcard1, action_object=wizcard2)
    notify.send(wizcard2.user, recipient=source_user,
                verb='wizconnection request trusted', 
                target=wizcard2, action_object=wizcard1)

def exchange_explicit(wizcard1, wizcard2):
    source_user = wizcard1.user
    target_user = wizcard2.user

    #send a connection request
    try:
        # If there's a wizconnection request from the other user accept it.
        accept_wizconnection(wizcard2, wizcard1)
    except Http404:
        # If we already have an active wizconnection request IntegrityError
        # will be raised and the transaction will be rolled back.
        try: 
            wizconnection = WizConnectionRequest.objects.create(
                from_wizcard=wizcard1,
                to_wizcard=wizcard2,
                message="wizconnection request") 
            #Q this to the receiver 
            notify.send(source_user, recipient=target_user, 
                        verb='wizconnection request untrusted', 
                        target=wizcard1, action_object=wizcard2)
        except: #AA: TODO: Put integrity error
            #nothing to do, just return silently
            pass 


def exchange(wizcard1, wizcard2, implicit):
    #create bidir cardship
    ret = dict(Error="OK", Description="")
    if Wizcard.objects.are_wizconnections(wizcard1, wizcard2):
        ret['Error'] = 2
        ret['Description'] = "Already connected to user"
    elif implicit:
        exchange_implicit(wizcard1, wizcard2)
    else:
        exchange_explicit(wizcard1, wizcard2)
    return ret

def update_wizconnection(wizcard1, wizcard2):
    notify.send(wizcard1.user, recipient=wizcard2.user,
                verb='wizcard update',
                target=wizcard1, action_object=wizcard2)
    


def find_users(userID, name, phone, email):
    #name can be first name, last name or even combined
    #any of the arguments may be null
    qlist = []

    if name != None:
        split = name.split()
        for n in split:
            name_result = (Q(first_name__icontains=n) | Q(last_name__icontains=n))
            qlist.append(name_result)

    #phone
    if phone != None:
        phone_result = (Q(phone1__contains=phone) | Q(phone2__contains=phone))
        qlist.append(phone_result)

    #email
    if email != None:
        email_result = Q(email=email)
        qlist.append(email_result)

    result = Wizcard.objects.filter(reduce(operator.or_, qlist)).exclude(user_id=userID)

    return result, len(result)

#Geohash related stuff

def create_geohash(lat, lng):
    encode = geohash.encode(lat, lng)
    print 'geohash encoded [{lat}, {lng}] to {encode}'.format (lat=lat, lng=lng, encode=encode)
    return encode

def lookup_closest_n(tree, key, n):
    return tree.longest_prefix_item(key)
