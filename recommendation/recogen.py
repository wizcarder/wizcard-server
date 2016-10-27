#import ...
import os
import sys
from datetime import datetime, timedelta
from django.utils import timezone
import time
import logging
import daemon
import re
import json

proj_path="."

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wizcard.settings")
sys.path.append(proj_path)
sys.path.append("..")
sys.path.append("../location_service")

from rabbit_service.server import RabbitServer, rconfig
from lib import wizlib

from django.core.wsgi import get_wsgi_application
from userprofile.models import *
from recommendation.models import *
application = get_wsgi_application()

#logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
logger = logging.getLogger('RecoGen')

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

# Interval between running recommendations fully

RECO_INTERVAL = 1


def isValidPhone(phonenum):

    if re.match("\+?\d{10,}",str(phonenum)):
        return True
    else:
        return False



def setupLogger(target='trigger'):
    logger.setLevel(logging.DEBUG)
    LOG_FILENAME = "./log/recogen" + "_" + target + ".log"

    # Add the log message handler to the logger
    handler = logging.handlers.RotatingFileHandler(
        LOG_FILENAME, maxBytes=1000000, backupCount=5)

    logger.addHandler(handler)



class RecoModel(object):

    def __init__(self,user):
        self.recotarget = user
        self.recomodel = None

    def putReco(self, rectype, score, object_id):
        recnew, created = Recommendation.objects.get_or_create(reco_content_type=ContentType.objects.get(model=rectype),
                                                               reco_object_id=object_id)

        recuser, ucreated = UserRecommendation.objects.get_or_create(user=self.recotarget, reco=recnew)

        if ucreated:
            recuser.useraction = 3
            recuser.save()

        recmeta, mcreated = RecommenderMeta.objects.get_or_create(recomodel=self.recomodel, userrecommend=recuser)
        recmeta.modelscore = score
        recmeta.save()
        
        #Update scores across all recommendations for this UserRecommendation object
        recuser.updateScore()
        recuser.save()


class ABReco (RecoModel):

    def __init__(self, user):
        #RecoModel.__init__(user)
        super(ABReco, self).__init__(user)
        self.recomodel = 0

    @property
    def getData(self):
        abentries = map(lambda x: x.ab_entry, AB_User.objects.filter(user=self.recotarget))
        if not abentries:
            return {}

        #Check if this user has a active wizcard
        try:
            twizcard = self.recotarget.wizcard
        except:
            return

        # Get all the wizcards connected to this user who has a wizcard
        wizusers = map(lambda x: x.user, self.recotarget.wizcard.get_connections())

        for entry in abentries:

            #Get all the users who have this abentry
            users = map(lambda x: x.user, AB_User.objects.filter(ab_entry=entry))

            if not entry.get_phone() and not entry.get_email():
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
                    logger.info("Adding Reco " + str(w1.pk) + " for " + self.recotarget.username)

                    self.putReco('wizcard', 2, w1.pk)
                    continue

            #Now it can only be addressbook
            recotype = 'addressbook'
            score = 0
            for user in users:
                #Checking if the AB entry is in my wizconnections then its a common entry
                if user in wizusers:
                    score += 2

            if entry.get_phone() and entry.get_email():
                logger.debug("Adding Reco " + entry.get_phone() + " for " + entry.get_email() + user.username)
                score += 1

            if entry.is_phone_final():
                score += 0.5

            if entry.is_email_final():
                score += 0.5

            if entry.is_name_final():
                score += 0.5

            # This includes all AB entries - Might be too much need to take a call??
            if (entry.get_phone() and isValidPhone(entry.get_phone())) or entry.get_email():
                score += 0.1

            logger.debug("Adding Reco " + str(entry.pk) + " for " + user.username)
            self.putReco(recotype, score, entry.pk)


class WizReco(RecoModel):

    def __init__(self, user):
        super(WizReco,self).__init__(user)
        self.recomodel = 1

    def getData(self):
        
        targetwizcard = None
        try:
            targetwizcard = self.recotarget.wizcard
        except:
            return
        recodict = dict()

        for hop1 in targetwizcard.get_connections():
            for hop2 in hop1.get_connections():
                # Eliminate the self wizcard
                if targetwizcard.phone != hop2.phone:
                    if hop2.pk in recodict.keys():
                        recodict[hop2.pk] += 1
                    else:
                        recodict[hop2.pk] = 1

        for wizreco in recodict.keys():
            if recodict[wizreco] == 1:
                continue

            self.putReco("wizcard", 10 * recodict[wizreco], wizreco)


class RecoRunner(RabbitServer):

    def __init__(self, *args, **kwargs):
        if args or kwargs:
            super(RecoRunner, self).__init__(*args, **kwargs)

        self.recorunners = {
             ABRECO: self.run_abreco,
             WIZRECO: self.run_wizreco,
             ALLRECO: self.run_allreco,
         }

    def runreco(self, target, torun):
        if target == 'full':
            i = 0
            while True:
                tdelta = timezone.timedelta(minutes = RECO_INTERVAL)
                current_time = timezone.now()
                checktime = current_time - tdelta
                time_str = checktime.strftime("%a, %d %b %Y %H:%M:%S +0000")
                logger.info(time_str)
                qs = UserProfile.objects.filter(reco_generated_at__lt=checktime, pk__gte = i * 100, pk__lt = (i+1) * 100)
                #qs = User.objects.filter(pk__gte = i * 100, pk__lt = (i+1) * 100)
                if qs:
                    for rec in qs:
                        self.recorunners[torun](rec.user.id)
                else:
                    break

                i += 1
        else:
            tdelta = timezone.timedelta(minutes = 5)
            current_time = timezone.now()
            checktime = current_time - tdelta
            try:
                qs = UserProfile.objects.get(reco_generated_at__lt=checktime, user=User.objects.get(id=target))
                self.recorunners[torun](target)
            except:
                return

    def run_abreco(self, target):
        tuser = None
        try:
            tuser = User.objects.get(id=target)
        except:
            pass
        if tuser:
            abreco_inst = ABReco(tuser)
            recos = abreco_inst.getData

    def run_wizreco(self, target):
        tuser = None
        try:
            tuser = User.objects.get(id=target)
        except:
            pass
        if tuser:
            wizreco_inst = WizReco(tuser)
            wizreco_inst.getData()

    def updateRecoTime(self, target):
        uprofile = User.objects.get(id=target).profile
        uprofile.reco_generated_at = timezone.now()
        uprofile.save()

    def run_allreco(self, target):
        self.run_abreco(target)
        self.run_wizreco(target)
        self.updateRecoTime(target)

    def on_message(self, ch, basic_deliver, props, body):
        logger.info('Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, props.app_id, body)
        args = json.loads(body)
        fn = args.pop('fn')
        rpc = args.pop('rpc', False)
        target = args.pop('target')
        self.runreco(target=target, torun=fn)
        self.acknowledge_message(basic_deliver.delivery_tag)


def main():

    isdaemon = False
    fullrun = False
    QCONFIG = rconfig.RECO_TRIGGER_CONFIG
    for params in sys.argv:
        if params == '--D' or params == '-daemon':
            isdaemon = True
        if params == 'trigger':
            QCONFIG = rconfig.RECO_TRIGGER_CONFIG
        if params == 'full':
            fullrun = True

    if fullrun:
        setupLogger(target='full')
        ts = RecoRunner()
        ts.runreco('full', ALLRECO)

    else:
        setupLogger(target='trigger')
        ts = RecoRunner(**QCONFIG)
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





