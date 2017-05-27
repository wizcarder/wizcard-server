from django.db import models
from django.contrib.auth.models import User
from base.custom_storage import WizcardQueuedS3BotoStorage
from base.custom_field import WizcardQueuedFileField
from base.char_trunc import TruncatingCharField
from base.emailField import EmailField
from base.cctx import ConnectionContext
from lib.preserialize.serialize import serialize
from wizserver import fields
from lib.ocr import OCR
from picklefield.fields import PickledObjectField

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
    invited = models.BooleanField(default=False)
    f_bizcard_image = WizcardQueuedFileField(upload_to="deadcards",
                                            storage=WizcardQueuedS3BotoStorage(delayed=False))
    activated = models.BooleanField(default=False)
    cctx = PickledObjectField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

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
        result = ocr.process(self.f_bizcard_image.local_path())

        self.first_name = result.get('first_name', "")
        self.last_name = result.get('last_name', "")
        self.phone = result.get('phone', "")
        self.email = result.get('email', "")
        self.company = result.get('company', "")
        self.title = result.get('job', "")
        self.web = result.get('web', "")
        self.cctx = ConnectionContext()
        self.save()

    def get_deadcard_cc(self):
        cc = dict()
        cc['phone'] = self.phone
        cc['email'] = self.email
        cc['company'] = self.company
        cc['title'] = self.title
        cc['web'] = self.web
        cc['card_url'] = self.deadcard_url()
        return cc

    def deadcard_url(self):
        return self.f_bizcard_image.remote_url()

    def created_on(self):
        return self.created.strftime("%d %B %Y")

    def set_context(self, cctx):
        self.cctx = cctx
        self.save()

    def get_context(self):
        return self.cctx

    def get_deadcard_context(self):
        return dict(description = self.cctx.description, notes = self.cctx.notes, created = self.created_on())


    def fix_context(self):
        if not self.cctx:
            self.cctx = ConnectionContext(asset_obj=self)

        if hasattr(self.cctx, '_usercctx'):
            if type(self.cctx.notes) is not dict:
                old_notes = self.cctx.notes
                self.cctx._usercctx = dict(
                    notes=dict(
                        note=old_notes,
                        last_saved=self.created.strftime("%d %B %Y")
                    )
                )
        else:
            self.cctx._usercctx = dict(
                notes=dict(
                    note="",
                    last_saved=self.created.strftime("%d %B %Y")
                )
            )
        self.save()

    #AA:TODO refactor. This should reuse CC model
    def serialize(self):
        wc = serialize(self, **fields.dead_cards_wizcard_template)
        return wc
