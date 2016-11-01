"""
.. autoclass:: Recommendation
    :members:

.. autoclass:: UserRecommendation
    :members:

.. autoclass:: RecommenderMeta
    :members:

"""
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from recommendation.signals import genreco
from wizcardship.models import Wizcard
from userprofile.models import AddressBook
from recommendation.tasks import addtoQtask
import logging

# Create your models here.

logger = logging.getLogger(__name__)

#AA: COmment: Have a manager class for below, put all global stuff (like serialization) in here
# things that operate over all instances (ie, exist at the table level) should be in the manager.
# generation of reco as another example. We will need to use celery to split up the DB into
# splices and run recos...enabler methods for all that potentially goes here


class Recommendation(models.Model):
    reco_content_type = models.ForeignKey(ContentType, related_name="reco")
    reco_object_id = models.PositiveIntegerField()
    reco = generic.GenericForeignKey('reco_content_type', 'reco_object_id')
    recommendation_for = models.ManyToManyField(User, through='UserRecommendation', symmetrical=False)

    def getRecoObject(self):
        pass

# check right hand side for the PEP warnings (too many blank lines, space after , 
# AA: Comment: Keep all models together

# AA: This needs to be refactored. I'll take care of it. Lets use LocationServiceClient and Server for this.
# I'll abstract it out so that it can be used as a platform layer

def addtoQ(**kwargs):
    logger.debug("CAll back in recommendation worked")
    kwargs.pop('signal', None)
    recotarget = kwargs.pop('recotarget')
    addtoQtask(recotarget)


# AA: Signal connect goes in the end of the file
genreco.connect(addtoQ, dispatch_uid='recommendation.models.recommendation')


class UserRecommendation(models.Model):

    Viewed = 0
    Acted = 1
    Dismissed = 2
    New = 3

    MODELS = (
        (0, 'AB_RECO'), 
        (1, 'WIZCONNECTIONS_RECO')
    )

    ACTIONS = (

        (Viewed, 'VIEWED'), 
        (Acted, 'ACTED'), 
        (Dismissed, 'DISMISSED'), 
	    (New, 'NEW'), 
    )
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    reco = models.ForeignKey(Recommendation, related_name='user_recos')
    useraction = models.PositiveSmallIntegerField(choices=ACTIONS, default = New)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    lastaction_time = models.DateTimeField(auto_now=True)

    def getReco(self):
        reco_list = []
        reco_dict = dict()
        if self.reco.reco_content_type == ContentType.objects.get(model='addressbook'):
            ab_object = AddressBook.objects.get(pk=self.reco.reco_object_id)

            # AA: COmments directly calling serialize is not correct and prone to errors. This has to go
            # via a custom serialize with the fields specifically called out.

            # also why is serialize being done here ? it's best to do it in the end at the
            # reco_dict level. This way is very hacky. You want to extract the appropriate params
            # out from AB object (Via an method in AB Object) and use that here instead of serialize

            # lastly, wouldn't the type tell the app what kind of reco it is ? shouldn't have the key called
            # 'addressbook' and 'wizcard'...should be a common name
            reco_dict['addressbook'] = ab_object.serialize()
            reco_dict['type'] = self.reco.reco_content_type.model
            reco_dict['recoid'] = self.pk
        if self.reco.reco_content_type == ContentType.objects.get(model='wizcard'):
            w_object = Wizcard.objects.get(pk=self.reco.reco_object_id)
            reco_dict['wizcard'] = w_object.serialize()
            reco_dict['type'] = self.reco.reco_content_type.model
            reco_dict['recoid'] = self.pk

        if self.reco.reco_content_type == ContentType.objects.get(model='userprofile'):
            pass

        return reco_dict


    def updateScore(self):
        metaobjects = self.reco_meta.all()

        self.score = 0

        for obj in metaobjects:
            self.score += obj.modelscore

        self.save()

    def setAction(self, action=New):

        self.useraction = action
        if action == Viewed:
            self.score = 1
        self.save()


class RecommenderMeta(models.Model):
    MODELS = (
        (0, 'AB_RECO'), 
        (1, 'WIZCONNECTIONS_RECO')
    )
    modelscore = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    recomodel = models.IntegerField(choices=MODELS)
    userrecommend = models.ForeignKey(UserRecommendation, related_name='reco_meta')
