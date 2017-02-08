"""
.. autoclass:: EmailAndPush
    :members:
"""

from django.db import models
from wizcardship.models import Wizcard
from base.emailField import EmailField
import datetime

# Create your models here.


class EmailAndPush(models.Model):
    NEWUSER = 1
    INVITED = 2
    SCANNED = 3
    NEWRECOMMENDATION = 4
    MISSINGU = 5
    JOINUS = 6
    DIGEST = 7
    EVENTS = (
        (NEWUSER, 'NEWUSER'),
        (INVITED, 'INVITED'),
        (SCANNED, 'SCANNED'),
        (NEWRECOMMENDATION, 'RECOMMENDATION'),
        (MISSINGU, 'MISSINGU'),
        (JOINUS, 'JOINUS'),
        (DIGEST, 'DIGEST')
    )
    wizcard = models.ForeignKey(Wizcard, related_name='email_and_push')
    event = models.PositiveSmallIntegerField(choices=EVENTS)
    to = EmailField(blank=True)
    last_sent = models.DateTimeField(blank=True,null=True)
