from django.db import models
from django.contrib.auth.models import User
from base.custom_storage import WizcardQueuedS3BotoStorage
from base.custom_field import WizcardQueuedFileField
from lib.preserialize.serialize import serialize
from wizserver import fields
from lib.ocr import OCR
import pdb

# Create your models here.
class DeadCardsManager(models.Manager):
    def serialize(self, deadcards):
        #AA: todo
        return serialize(deadcards, **fields.dead_cards_wizcard_template)

#AA:TODO refactor. This should reuse CC model
class DeadCards(models.Model):
    user = models.ForeignKey(User, related_name="dead_cards")
    first_name = models.CharField(max_length=40, blank=True)
    last_name = models.CharField(max_length=40, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    company = models.CharField(max_length=40, blank=True)
    title = models.CharField(max_length=200, blank=True)
    web = models.CharField(max_length=200, blank=True)
    f_bizCardImage = WizcardQueuedFileField(upload_to="deadcards",
                                            storage=WizcardQueuedS3BotoStorage(delayed=False))

    objects = DeadCardsManager()

    def __unicode__(self):
        return (u'%(user)s\'s dead card: %(title)s@ %(company)s \n') % \
               {'user': unicode(self.user),
                'title': unicode(self.title),
                'company': unicode(self.company)}

    def delete(self, *args, **kwargs):
        # incomplete...need to take care of storage cleanup and/or, not deleting
        # but setting a flag instead
        pdb.set_trace()
        super(DeadCards, self).delete(*args, **kwargs)

    def recognize(self):
        ocr = OCR()
        result = ocr.process(self.f_bizCardImage.local_path())

        self.first_name = result.get('first_name', "")
        self.last_name = result.get('last_name', "")
        self.phone = result.get('phone', "")
        self.email = result.get('email', "")
        self.company = result.get('company', "")
        self.title = result.get('job', "")
        self.web = result.get('web', "")
        self.save()

    def get_deadcard_cc(self):
        cc = dict()
        cc['phone'] = self.phone
        cc['email'] = self.email
        cc['company'] = self.company
        cc['title'] = self.title
        cc['web'] = self.web
        cc['url'] = self.deadcard_url()
        return cc

    def deadcard_url(self):
        return self.f_bizCardImage.remote_url()

    #AA:TODO refactor. This should reuse CC model
    def serialize(self):
        wc = serialize(self, **fields.dead_cards_wizcard_template)
        return wc
