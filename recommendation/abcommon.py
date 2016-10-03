#import ...
from collections import OrderedDict
import os,sys
import logging
import pdb
from decimal import *

proj_path="."

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wizcard.settings")
sys.path.append(proj_path)
from wizserver import verbs
from wizserver import fields
from wizcardship.models import WizConnectionRequest,Wizcard
from base.cctx import *
from lib.preserialize.serialize import serialize
import pika
import json

from django.core.wsgi import get_wsgi_application
from userprofile.models import *
from recommendation.models import *
application = get_wsgi_application()

from django.core.cache import cache

logger = logging.getLogger(__name__)

from lib.preserialize.serialize import serialize



class ABReco (object) :

    def __init__(self,user):
        self.recotarget = user
        self.recomodel = 0

    def putReco(self, rectype, score, object_id):
        recnew, created = Recommendation.objects.get_or_create(reco_content_type=ContentType.objects.get(model=rectype),
                                                               reco_object_id=object_id)
        recuser, created = UserRecommendation.objects.get_or_create(user=self.recotarget, reco=recnew)



        if created:
            recuser.useraction = 3
            recuser.score = score
            recuser.save()
        else:
            recuser.score = recuser.score + Decimal(score)
            recuser.save()

        recmeta,created = RecommenderMeta.objects.get_or_create(recomodel=self.recomodel, userrecommend=recuser)
        recmeta.modelscore = score
        recmeta.save()

    def getData(self):
        abentries = map(lambda x:x.ab_entry,AB_User.objects.filter(user=self.recotarget))
        if not abentries:
            return {}

        wizusers = map(lambda x:x.user,self.recotarget.wizcard.get_connections())

        for entry in abentries:
            users = map(lambda x: x.user,AB_User.objects.filter(ab_entry=entry))

            if not entry.get_phone() and not  entry.get_email():
                continue

            entry_username = entry.get_phone() + '@wizcard.com'

            # Eliminate Self from the recommendation
            if entry_username == self.recotarget.username:
                continue

            w1 = UserProfile.objects.check_user_exists(verbs.INVITE_VERBS[verbs.SMS_INVITE], entry.get_phone())

            if not w1 and entry.get_email():
                w1 = UserProfile.objects.check_user_exists(verbs.INVITE_VERBS[verbs.EMAIL_INVITE], entry.get_email())

            # Eliminate Self in recommendation
            if self.recotarget.id == w1.id:
                continue

            if w1:
                if not self.recotarget.wizcard.get_relationship(w1):
                    print "Adding Reco " + str(w1.pk) + " for " + self.recotarget.username

                    self.putReco('wizcard',2,w1.pk)
                    continue

            #Now it can only be addressbook
            recotype = 'addressbook'
            score = 0
            for user in users:
                if user in wizusers:
                    print "Adding Reco " + str(entry.pk) + " for " + user.username
                    score = score + 2



            if entry.get_phone() and entry.get_email():
                print "Adding Reco " + str(entry.pk) + " for " + user.username
                score = score + 1

            if entry.is_phone_final():
                score = score + 0.5

            if entry.is_email_final():
                score = score + 0.5

            if entry.is_name_final():
                score = score + 0.5

            if entry.get_phone() or entry.get_email():
                score = score + 0.1

            print "Adding Reco " + str(entry.pk) + " for " + user.username
            self.putReco(recotype,score,entry.pk)



#        self.reco = OrderedDict(sorted(self.reco.items(), key=lambda x: x[1]), reverse=True)






class WizReco(object):
    def __init__(self,user):
        self.recotarget = user
        self.recomodel = 1

    def getData(self):
        targetwizcard = self.recotarget.wizcard

        recodict = dict()

        for hop1 in targetwizcard.get_connections():
            for hop2 in hop1.get_connections():
            # Eliminate the self wizcard
                if targetwizcard.phone != hop2.phone:
                    if hop2.user.pk in recodict.keys():
                        recodict[hop2.pk] +=  1
                    else:
                        recodict[hop2.pk] = 1

        for wizreco in recodict.keys():
            if recodict[wizreco] == 1:
                continue

            self.putReco("wizcard", 10 * self.reco[wizreco], wizreco)


    def putData(self):

        recnew, created = Recommendation.objects.get_or_create(reco_content_type=ContentType.objects.get(model=rectype),
                                                               reco_object_id=object_id)

        recuser, created = UserRecommendation.objects.get_or_create(user=self.recotarget, reco=recnew)

        if created:
            recuser.useraction = 3
            recuser.score = score
            recuser.save()
        else:
            recuser.score = recuser.score + Decimal(score)
            recuser.save()

        recmeta, created = RecommenderMeta.objects.get_or_create(recomodel=self.recomodel, userrecommend=recuser)
        recmeta.modelscore = score
        recmeta.save()


def callback(ch, method, properties, body):
    body_data = json.loads(body)
    pdb.set_trace()

    wuser = ""
    rmodel = ""
    if body_data.has_key('recmodel'):
        rmodel = body_data['recmodel']
    else:
        print "No model specified in message: Reco generation not happening"
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return


    if rmodel != "all" and body_data.has_key('recotarget'):
        wuser = Wizcard.objects.get(id=int(body_data['recotarget'])).user
        if not wuser:
            print "No user specified in message: Reco generation not happening"
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return


    if rmodel == 'ABReco':
        treco = ABReco(wuser)
        reco = treco.getData()
    elif rmodel == 'WizReco':
        treco = WizReco(wuser)
        reco = treco.getData()
    elif rmodel =='all':
        reco = dict()

        wall = Wizcard.objects.all()

        for w in wall:
            treco = WizReco(w.user)
            reco = treco.getData()

        for w in wall:
            treco = ABReco(w.user)
            print "Generating Reco for " + w.user.username
            reco = treco.getData()

    ch.basic_ack(delivery_tag=method.delivery_tag)



if __name__ == "__main__":
    validqs = ['recoall', 'recotrigger']
    if len(sys.argv) > 1:

        qname = sys.argv[1]
    else:
        qname = 'recoall'

    if qname not in validqs:
        sys.stderr.write("Invalid Q Name %s\n", qname)
        exit(1)

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=qname)
    channel.basic_consume(callback, queue=qname)
    channel.start_consuming()



'''

'''
