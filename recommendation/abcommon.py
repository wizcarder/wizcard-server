#import ...
from collections import OrderedDict
import os,sys
import logging

proj_path="/Users/kappu/Documents/Anand/wizcard-server"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wizcard.settings")
sys.path.append(proj_path)
from wizserver import verbs
from wizserver import fields
from wizcardship.models import WizConnectionRequest,Wizcard
from base.cctx import *
from lib.preserialize.serialize import serialize

from django.core.wsgi import get_wsgi_application
from userprofile.models import *
application = get_wsgi_application()

from django.core.cache import cache

logger = logging.getLogger(__name__)

from lib.preserialize.serialize import serialize

class AbCommon (object) :

    def __init__(self,user):
        self.recotarget = user


    def getData(self):
        #abmap = {x:len(FutureUser.objects.getWizcarders(x)) for x in user.getaddressbook()}
        #return abmap
        return {'Anand': 5, 'Baskar' : 4, 'Catherine': 3}

    def genReco(self,data):
        abreco = OrderedDict(sorted(data.items(), key=lambda x: x[1]), reverse=True)

class WizReco(object):
    def __init__(self,user):
        self.recotarget = user
        self.reco = dict()

    def getData(self):
        targetwizcard = user.wizcard
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

wall = Wizcard.objects.all()
for w in wall:
    treco = WizReco(w.user)
    reco[w.userid]=treco.getData()













