"""
.. autoclass:: Recommendation
    :members:

.. autoclass:: UserRecommendation
    :members:

.. autoclass:: RecommenderMeta
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
from notifications.tasks import pushNotificationToApp
import logging
import pdb

# Create your models here.


class Recommendation(models.Model):
    reco_content_type = models.ForeignKey(ContentType,related_name="reco")
    reco_object_id = models.PositiveIntegerField()
    reco = generic.GenericForeignKey('reco_content_type','reco_object_id')
    recommendation_for = models.ManyToManyField(User,through='UserRecommendation',symmetrical=False)
    isactive = models.BooleanField(default=False)


class UserRecommendation(models.Model):

    ACTIONS = (
        (0, 'IGNORE'),
        (1, 'CLICK'),
        (2, 'CLICKANDINVITE')
    )
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    reco = models.ForeignKey(Recommendation)

    useraction = models.PositiveSmallIntegerField(choices=ACTIONS)




class RecommenderMeta(models.Model):
    MODELS = (
        (0,'AB_RECO'),
        (1, 'WIZCONNECTIONS_RECO')
    )
    score = models.DecimalField(max_digits=5, decimal_places=2)
    recomodel = models.IntegerField(choices=MODELS)
    userrecommend = models.ForeignKey(UserRecommendation)
















