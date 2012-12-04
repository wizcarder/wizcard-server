"""
.. autoclass:: WizConnectionRequest
    :members:

.. autoclass:: WizcardManager
    :members:

.. autoclass:: Wizcard
    :members:

.. autoclass:: UserBlocks
    :members:
"""


import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
import signals
import pdb
from django.db.models import Q
from django.core.files.base import ContentFile
#from django.db.models import ImageField

class WizcardManager(models.Manager):
    def except_wizcard(self, except_user):
        qs = Wizcard.objects.filter(~Q(user=except_user))
        return qs 
		
    def wizconnections_of(self, user, shuffle=False):
        qs = User.objects.filter(wizcard__wizconnections__user=user)
        if shuffle:
            qs = qs.order_by('?')
        return qs

    def are_wizconnections(self, wizcard1, wizcard2):
        return bool((wizcard1.wizconnections.filter(
            id=wizcard2.id)).exists())

    def wizconnection_req_clear(self, from_wizcard, to_wizcard):
        WizConnectionRequest.objects.filter(from_wizcard=from_wizcard,
                                            to_wizcard=to_wizcard).delete()

		
    def becard(self, wizcard1, wizcard2):
        wizcard1.wizconnections.add(wizcard2)
        # Now that user1 accepted user2's card request we should delete any
        # request by user1 to user2 so that we don't have ambiguous data
        WizConnectionRequest.objects.filter(from_wizcard=wizcard1,
                                            to_wizcard=wizcard2).delete()

    def uncard(self, wizcard1, wizcard2):
        # Break cardship link between users
        wizcard1.wizconnections.remove(wizcard2)
        # Delete Wizcconnection request as well
        self.wizconnection_req_clear(wizcard1, wizcard2)
        self.wizconnection_req_clear(wizcard2, wizcard1)

class Wizcard(models.Model):
    user = models.ForeignKey(User, related_name='wizcards')
    wizconnections = models.ManyToManyField('self', symmetrical=True, blank=True)
    first_name = models.CharField(max_length=40, blank=True)
    last_name = models.CharField(max_length=40, blank=True)
    company = models.CharField(max_length=40, blank=True)
    title = models.CharField(max_length=200, blank=True)
    phone1 = models.CharField(max_length=20, blank=True)
    phone2 = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address_street1 = models.CharField(max_length=40, blank=True)
    address_city = models.CharField(max_length=40, blank=True)
    address_state = models.CharField(max_length = 20, blank=True)
    address_country = models.CharField(max_length = 20, blank=True)
    address_zip = models.CharField(max_length = 20, blank=True)
    isDefaultCard = models.BooleanField(default=False)
    #media objects
    #AA:TODO: This(image/video management) is quite primitive
    thumbnailImage = models.ImageField(upload_to="image/")
    video = models.FileField(upload_to="video/")



    objects = WizcardManager()

    class Meta:
        verbose_name = _(u'wizcard')
        verbose_name_plural = _(u'wizcards')

    def __unicode__(self):
        return _(u'%(user)s\'s wizcard') % {'user': unicode(self.user)}

    def wizconnection_count(self):
        return self.wizconnections.count()
    wizconnection_count.short_description = _(u'Cards count')

    def wizconnection_summary(self, count=7):
        wizconnection_list = self.wizconnections.all().select_related(depth=1)[:count]
        return u'[%s%s]' % (u', '.join(unicode(f.user) for f in wizconnection_list),
                            u', ...' if self.wizconnection_count() > count else u'')
    wizconnection_summary.short_description = _(u'Summary of wizconnections')

    def set_default(self):
        self.isDefaultCard = True
    
    def clear_default(self):
        self.isDefaultCard = False
        self.save()

    def flood(self):
        from wizserver import wizlib
        for wizcard in self.wizconnections.all():
            wizlib.exchange_implicit(self, wizcard)

class WizConnectionRequest(models.Model):
    from_wizcard = models.ForeignKey(Wizcard, related_name="invitations_from")
    to_wizcard = models.ForeignKey(Wizcard, related_name="invitations_to")
    message = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(default=datetime.datetime.now,
                                   editable=False)
    accepted = models.BooleanField(default=False)

    class Meta:
        verbose_name = _(u'wizconnection request')
        verbose_name_plural = _(u'wizconnection requests')
        unique_together = (('to_wizcard', 'from_wizcard'),)

    def __unicode__(self):
        return _(u'%(from_wizcard)s wants to be wizconnections with %(to_wizcard)s') % \
                    {'from_wizcard': unicode(self.from_wizcard),
                     'to_wizcard': unicode(self.to_wizcard)}

    def accept(self):
        Wizcard.objects.becard(self.from_wizcard, self.to_wizcard)
        self.accepted = True
        self.save()
        signals.wizcardship_accepted.send(sender=self)

    def decline(self):
        signals.wizcardship_declined.send(sender=self)
        self.delete()

    def cancel(self):
        signals.wizcardship_cancelled.send(sender=self)
        self.delete()




class UserBlocks(models.Model):
    user = models.ForeignKey(User, related_name='user_blocks')
    blocks = models.ManyToManyField(User, related_name='blocked_by_set')

    class Meta:
        verbose_name = verbose_name_plural = _(u'user blocks')

    def __unicode__(self):
        return _(u'Users blocked by %(user)s') % {'user': unicode(self.user)}

    def block_count(self):
        return self.blocks.count()
    block_count.short_description = _(u'Blocks count')

    def block_summary(self, count=7):
        block_list = self.blocks.all()[:count]
        return u'[%s%s]' % (u', '.join(unicode(user) for user in block_list),
                            u', ...' if self.block_count() > count else u'')
    block_summary.short_description = _(u'Summary of blocks')


# Signal connections
#models.signals.post_save.connect(signals.create_wizcardship_instance,
#                                 sender=User,
#                                 dispatch_uid='cards.signals.create_' \
#                                              'wizcardship_instance')
#models.signals.post_save.connect(signals.create_userblocks_instance,
#                                 sender=User,
#                                 dispatch_uid='cards.signals.create_' \
#                                              'userblocks_instance')
