from django.db import models
from django.contrib.auth.models import User
from base.custom_storage import WizcardQueuedS3BotoStorage
from base.custom_field import WizcardQueuedFileField
from base.char_trunc import TruncatingCharField
from base.emailField import EmailField
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
    first_name = TruncatingCharField(max_length=40, blank=True)
    last_name = TruncatingCharField(max_length=40, blank=True)
    phone = TruncatingCharField(max_length=20, blank=True)
    email = EmailField(blank=True)
    company = TruncatingCharField(max_length=40, blank=True)
    title = TruncatingCharField(max_length=200, blank=True)
    web = TruncatingCharField(max_length=200, blank=True)
    f_bizCardImage = WizcardQueuedFileField(upload_to="deadcards",
                                            storage=WizcardQueuedS3BotoStorage(delayed=False))
    activated = models.BooleanField(default=False)

    objects = DeadCardsManager()

    def __unicode__(self):
        return (u'%(user)s\'s dead card: %(title)s@ %(company)s \n') % \
               {'user': unicode(self.user),
                'title': unicode(self.title),
                'company': unicode(self.company)}

    def delete(self, *args, **kwargs):
        # incomplete...need to take care of storage cleanup and/or, not deleting
        # but setting a flag instead
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
        cc['f_bizCardUrl'] = self.deadcard_url()
        return cc

    def deadcard_url(self):
        return self.f_bizCardImage.remote_url()

    #AA:TODO refactor. This should reuse CC model
    def serialize(self):
        wc = serialize(self, **fields.dead_cards_wizcard_template)
        return wc
