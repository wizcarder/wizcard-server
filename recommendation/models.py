"""
.. autoclass:: Recommendation
    :members:

.. autoclass:: UserRecommendation
    :members:

"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.utils import timezone
from django.conf import settings
from notifications.signals import notify
from recommendation.signals import genreco
from notifications.tasks import pushNotificationToApp
from wizcardship.models import Wizcard
from userprofile.models import AddressBook
from celery import shared_task
from recommendation.tasks import addtoQtask
import json
import logging
import pika

import pdb

# Create your models here.

logger = logging.getLogger(__name__)


class Recommendation(models.Model):
    reco_content_type = models.ForeignKey(ContentType,related_name="reco")
    reco_object_id = models.PositiveIntegerField()
    reco = generic.GenericForeignKey('reco_content_type','reco_object_id')
    recommendation_for = models.ManyToManyField(User,through='UserRecommendation',symmetrical=False)


    def getRecoObject(self):
        pass





def addtoQ(**kwargs):
    logger.debug("CAll back in recommendation worked")
    kwargs.pop('signal', None)
    recotarget = kwargs.pop('recotarget')
    recmodel = kwargs.pop('recmodel')
    addtoQtask.delay('rectrigger',recotarget,recmodel)


genreco.connect(addtoQ, dispatch_uid='recommendation.models.recommendation')





class UserRecommendation(models.Model):

    Viewed = 0
    Acted = 1
    Dismissed = 2
    New = 3

    MODELS = (
        (0,'AB_RECO'),
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
    reco = models.ForeignKey(Recommendation,related_name='user_recos')
    useraction = models.PositiveSmallIntegerField(choices=ACTIONS,default = New)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    lastaction_time = models.DateTimeField(auto_now=True)

    def getReco(self):
        reco_list = []
        reco_dict = dict()
        if self.reco.reco_content_type == ContentType.objects.get(model='addressbook'):
            ab_object = AddressBook.objects.get(pk=self.reco.reco_object_id)
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




    def setAction(self,action=New):

        self.useraction = action
        self.save()


class RecommenderMeta(models.Model):
    MODELS = (
        (0, 'AB_RECO'),
        (1, 'WIZCONNECTIONS_RECO')
    )
    modelscore = models.DecimalField(max_digits=5, decimal_places=2,default=0)
    recomodel = models.IntegerField(choices=MODELS)
    userrecommend = models.ForeignKey(UserRecommendation)





        



