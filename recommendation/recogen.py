#import ...
from collections import OrderedDict
import os,sys
import logging
import pdb
from decimal import *

proj_path="."

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wizcard.settings")
sys.path.append(proj_path)
sys.path.append("../wizcard-server")
sys.path.append("../wizcard-server/location_service")

from wizserver import verbs
from wizserver import fields
from wizcardship.models import WizConnectionRequest,Wizcard
from base.cctx import *
from lib.preserialize.serialize import serialize
from location_service.server import RabbitServer
from location_service import rconfig
import pika
import time
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

ABRECO = 0
WIZRECO = 1
ALLRECO = 2


class RecoModel(object):

    def __init__(self,user):
        self.recotarget = user
        self.recomodel = None

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

        recmeta, created = RecommenderMeta.objects.get_or_create(recomodel=self.recomodel, userrecommend=recuser)
        recmeta.modelscore = score
        recmeta.save()


class ABReco (RecoModel) :

    def __init__(self,user):
        #RecoModel.__init__(user)
        super(ABReco, self).__init__(user)
        self.recomodel = 0


    def getData(self):
        abentries = map(lambda x:x.ab_entry,AB_User.objects.filter(user=self.recotarget))
        if not abentries:
            return {}

        # Get all the wizcards connected to this user who has a wizcard
        wizusers = map(lambda x:x.user,self.recotarget.wizcard.get_connections())

        for entry in abentries:

            #Get all the users who have this abentry
            users = map(lambda x: x.user,AB_User.objects.filter(ab_entry=entry))

            if not entry.get_phone() and not  entry.get_email():
                continue

            entry_username = entry.get_phone() + '@wizcard.com'

            # Eliminate Self from the recommendation
            if entry_username == self.recotarget.username:
                continue

            # Check if the abentry is a wizcard user based on email and phone from the AB
            w1 = UserProfile.objects.check_user_exists(verbs.INVITE_VERBS[verbs.SMS_INVITE], entry.get_phone())

            if not w1 and entry.get_email():
                w1 = UserProfile.objects.check_user_exists(verbs.INVITE_VERBS[verbs.EMAIL_INVITE], entry.get_email())


            # Eliminate Self in recommendation
            if w1 and self.recotarget.id == w1.id:
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
                #Checking if the AB entry is in my wizconnections then its a common entry
                if user in wizusers:
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

            # This includes all AB entries - Might be too much need to take a call??
            if entry.get_phone() or entry.get_email():
                score = score + 0.1

            print "Adding Reco " + str(entry.pk) + " for " + user.username
            self.putReco(recotype,score,entry.pk)


class WizReco(RecoModel):

    def __init__(self,user):
        super(WizReco,self).__init__(user)
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


class RecoRunner(RabbitServer):

    def __init__(self, *args, **kwargs):
        super(RecoRunner, self).__init__(*args, **kwargs)

        self.recorunners = {
             ABRECO: self.run_abreco,
             WIZRECO: self.run_wizreco,
             ALLRECO : self.run_allreco,
         }


    def runreco(self,target,torun):
        if target == 'full':
            i = 0
            while True:
                qs = Wizcard.objects.filter(pk__gte = i * 100, pk__lt = (i+1) * 100)
                try:
                    for rec in qs:
                        self.recorunners[torun](rec.id)

                except Wizcard.DoesNotExist:
                    break

                i += 1
        else:

            self.recorunners[torun](target)

    def run_abreco(self,target):
        tuser = Wizcard.objects.get(id=target).user
        abreco_inst = ABReco(tuser)
        recos = abreco_inst.getData()

    def run_wizreco(self,target):
        tuser = Wizcard.objects.get(id=target).user
        wizreco_inst = WizReco(tuser)
        recos = wizreco_inst.getData()

    def run_allreco(self,target):
        self.run_abreco(target)
        self.run_wizreco(target)

    def on_message(self, ch, basic_deliver, props, body):
        logger.info('Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, props.app_id, body)
        args = json.loads(body)
        fn = args.pop('fn')
        rpc = args.pop('rpc', False)
        target = args.pop('target')
        response = self.runreco(target=target,torun=fn)
        self.acknowledge_message(basic_deliver.delivery_tag)






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


import daemon
def main():
    logging.basicConfig(level=logging.INFO)
    isdaemon = False
    for params in sys.argv:
        if params == '--D' or params == '-daemon':
            isdaemon = True

    ts = RecoRunner(**rconfig.RECO_Q_CONFIG)

    if isdaemon:
        with daemon.DaemonContext():
            ts.run()
    else:
        try:
            ts.run()
        except KeyboardInterrupt:
            ts.stop()





if __name__ == "__main__":

    main()


'''


    validqs = [ABRECO, WIZRECO, ALLRECO]

    if len(sys.argv) < 3:
        print "Usage recogen.py <wizcardid> <modelid[0,1,2]>"
        print "Running for all wizcards and generating all recos"
        print "Sleeping for 5 secs - Giving a chance to quit - Press Ctrl-C"
        time.sleep(5)
    else:
        wizcard_id = int(sys.argv[1])

        if len(sys.argv) > 1:
            qname = int(sys.argv[2])
        else:
            qname = ALLRECO

        if qname not in validqs:
            sys.stderr.write("Invalid Model Name " + str(qname) + "\n")
            exit(1)
        wall = Wizcard.objects.get(id=wizcard_id)

        recorunner = RunReco(wall,qname)
        recorunner.runreco()
'''





