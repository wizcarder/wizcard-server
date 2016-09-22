#import ...
from collections import OrderedDict
import os,sys
import logging

proj_path="."

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wizcard.settings")
sys.path.append(proj_path)
from wizserver import verbs
from wizserver import fields
from wizcardship.models import WizConnectionRequest,Wizcard
from base.cctx import *
from lib.preserialize.serialize import serialize

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

    def putReco(self, rectype, score, object_id):
        recnew, created = Recommendation.objects.get_or_create(reco_content_type=ContentType.objects.get(model=rectype),
                                                               reco_object_id=object_id)
        recuser, created = UserRecommendation.objects.get_or_create(user=self.recotarget, reco=recnew)
        if created:
            recuser.useraction = 3
            recuser.score = score
            recuser.recomodel = 0
            recuser.save()
        else:
            recuser.score += 2
            recuser.save()

    def getData(self):
        abentries = map(lambda x:x.ab_entry,AB_User.objects.filter(user=self.recotarget))
	if not abentries:
		return {}

        wizusers = map(lambda x:x.user,self.recotarget.wizcard.get_connections())

        for entry in abentries:
            users = map(lambda x: x.user,AB_User.objects.filter(ab_entry=entry))
            if not entry.get_phone() and not  entry.get_email():
                continue

	    if entry.get_phone():
	            w1 = UserProfile.objects.check_user_exists(verbs.INVITE_VERBS[verbs.SMS_INVITE], entry.get_phone())
            if not w1 and entry.get_email():
                w1 = UserProfile.objects.check_user_exists(verbs.INVITE_VERBS[verbs.EMAIL_INVITE], entry.get_email())
            if w1:
                if not self.recotarget.wizcard.get_relationship(w1):
		    print "Adding Reco " + str(w1.pk) + " for " + self.recotarget.username
                    self.putReco('wizcard',2,w1.pk)
		    continue
		

            for user in users:
                if user in wizusers:
		    print "Adding Reco " + str(entry.pk) + " for " + user.username
                    self.putReco('addressbook',3,entry.pk)


            if entry.get_phone() and entry.get_email():
		print "Adding Reco " + str(entry.pk) + " for " + user.username
                self.putReco('addressbook', 1,entry.pk)

            # THIS NEEDS TO BE A WIZCARD USER and not a AB entry
	
	    if entry.get_phone() or entry.get_email():
		print "Adding Reco " + str(entry.pk) + " for " + user.username
		self.putReco('addressbook',0.1,entry.pk)



#        self.reco = OrderedDict(sorted(self.reco.items(), key=lambda x: x[1]), reverse=True)



		


class WizReco(object):
    def __init__(self,user):
        self.recotarget = user
        self.reco = dict()

    def getData(self):
        targetwizcard = self.recotarget.wizcard
        for hop1 in targetwizcard.get_connections():
            for hop2 in hop1.get_connections():
            # Eliminate the self wizcard
                if targetwizcard.phone != hop2.phone:
                    if hop2.user in self.reco:
                        reco[hop2.user] = reco[hop2.user] + 1
                    else:
                        reco[hop2.user] = 1

        return self.reco



'''
# Initially was thinking of putting it in memcache
class RunReco (object) :
    def __init__(self,model,user):
        self.runmodel = AbCommon(user)
        self.reco = {}
        self.user = user

    def getReco(self):
            data = self.runmodel.getData()
            reco = self.runmodel.genReco(data)

    def putReco(self):
        value = serialize(reco)
        res = cache.set(self.user.pk,value)
        if res:
            logger.error("Cannot add value for user: %s" % self.user.pk)
        else:
            res = cache.get(self.user.pk)
            print res


recotarget = Wizcard.objects.get(id=1).user
reco = RunReco("AbCommon",recotarget)
reco.getReco()
reco.putReco()
'''
wall=[]
if len(sys.argv) > 1:
	wid = sys.argv[1]
	wall.append(Wizcard.objects.get(id=wid))

reco=dict()
if len(wall) == 0:
	wall = Wizcard.objects.all()
for w in wall:
    treco = WizReco(w.user)
    reco[w.user.pk]=treco.getData()


for w in wall:
    treco = ABReco(w.user)
    print "Generating Reco for " + w.user.username
    reco = treco.getData()
    '''
    for rec in reco.keys():

        recnew,created = Recommendation.objects.get_or_create(reco_content_type=ContentType.objects.get(model='addressbook'),reco_object_id=rec)
        recuser,created = UserRecommendation.objects.get_or_create(user=w.user,reco=recnew)
        if created:
            recuser.useraction = 3
            recuser.score = reco[rec]
            recuser.recomodel = 0
	    recuser.save()
        else:
            recuser.score = reco[rec]
	    recuser.save()
    '''













