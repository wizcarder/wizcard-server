from django.db import models
from django.contrib.auth.models import User
from wizcard.custom_storage import WizcardQueuedS3BotoStorage
from wizcard.custom_field import WizcardQueuedFileField
from lib.preserialize.serialize import serialize
from lib.ocr import OCR

# Create your models here.
class DeadCardsManager(models.Manager):
    def serialize(self, deadcards, template):
        return serialize(deadcards, **template)

class DeadCards(models.Model):
    user = models.ForeignKey(User, related_name="dead_cards")
    first_name = models.CharField(max_length=40, blank=True)
    last_name = models.CharField(max_length=40, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    company = models.CharField(max_length=40, blank=True)
    title = models.CharField(max_length=200, blank=True)
    web = models.CharField(max_length=200, blank=True)
    f_bizCardImage = WizcardQueuedFileField(upload_to="dead_cards/",
                         storage=WizcardQueuedS3BotoStorage(delayed=False))

    objects = DeadCardsManager()

    def __unicode__(self):
        return _(u'%(user)s\'s contact container: %(title)s@ %(company)s \n')\
                % {'user': unicode(self.wizcard.user), 'title': \
                unicode(self.title), 'company': unicode(self.company)}

    def recognize(self):
        ocr = OCR()
        result =  ocr.process(self.f_bizCardImage.path)

        self.first_name = result.get('first_name', None)
        self.last_name = result.get('last_name', None)
        self.phone = result.get('phone', None)
        self.email = result.get('email', None)
        self.company = result.get('company', None)
        self.title = result.get('title', None)
        self.web = result.get('web', None)
        self.save()
