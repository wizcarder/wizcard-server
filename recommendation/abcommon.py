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

# AA: Comments: check all the PEP warnings on the right side pane in pycharm.
# Basic Ones that should be clean are:
# 1) Tabs, Space (you'll see a yellow highlight in the editor on pycharm wherever those show up)
# 2) x, y) instead of x,y)
# 3) Line spacing...single line between methods and 2 lines between classes

# AA: Generic code architecture comment. The layout needs to be modular and extensible
# have a base class that defines the vectors for running a recommender, gettings its results, setting score logic etc
# have a singleton set that is used to register these recommenders
# from the recommenders perspective, it'll be anything that implements those vectors...when it inits, it'll register
# itself to the top level singleton

# running reco is to run the "run" vector in the base class...from here all things can be controlled...including
# things like whether it is to run the recommender in celery.as

# Other generic comment: I think your approach is to come up with a quick POC first and then iterate on top of it.
# I really feel taking a top down approach will payoff much quicker and cleaner. have the higher lever constructs,
# modularize it from the start...any interfaces that the app needs can be quickly mocked up within the stub methods.

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

	    if not w1:
		continue

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
                    if hop2.pk in recodict.keys():
                        recodict[hop2.pk] +=  1
                    else:
                        recodict[hop2.pk] = 1

        for wizreco in recodict.keys():
            if recodict[wizreco] == 1:
                continue

            self.putReco("wizcard", 10 * recodict[wizreco], wizreco)


    def putReco(self,rectype,score,object_id):

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


# AA COmments: I'll work on this. Will intergrate it with the existing client
def callback(ch, method, properties, body):
    body_data = json.loads(body)

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
# AA Comments: This doesn't look right...callback shouldn't be handling so much
# Also, can't load .all() like that into memory...wont scale
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
    validqs = ['recoall', 'rectrigger']
    if len(sys.argv) > 1:

        qname = sys.argv[1]
    else:
        qname = 'recoall'

    if qname not in validqs:
        sys.stderr.write("Invalid Q Name %s\n", qname)
        exit(1)

    wall = Wizcard.objects.all()

    for w in wall:
        treco = WizReco(w.user)
        reco = treco.getData()

    # AA COmments: Why twice ? Also, same comment as above. This needs to be more sophisticated.
    # Also...why would this be required at all ? Looks like it'll run only once in its lifetime.
    for w in wall:
        treco = ABReco(w.user)
        print "Generating Reco for " + w.user.username
        reco = treco.getData()

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=qname)
    print "Waiting for Q items"
    channel.basic_consume(callback, queue=qname)
    channel.start_consuming()



'''

'''
