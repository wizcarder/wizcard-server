from django.conf import settings
#from django.core.mail import EmailMultiAlternatives
from django.core.mail import EmailMessage
from django.template import Template, Context
from django.template.loader import render_to_string
import pdb
import logging

logger = logging.getLogger(__name__)


class Email(object):
    
    def __init__(self, to, subject):
        #self.to = to
        self.to = "anandramani98@gmail.com"
        self.subject = subject
        self._html = None
        self._text = None

    def _render(self, emailtemplate, context):
        return render_to_string(emailtemplate, context)

    def html(self, emailtemplate, context):
        self._html = self._render(emailtemplate, context)

    def text(self, emailtemplate, context):
        self._text = self._render(emailtemplate, context)

    def send(self, from_addr=None, fail_silently=False, attach=None):
        if isinstance(self.to, basestring):
            self.to = [self.to]
        if not from_addr:
            from_addr = getattr(settings, 'EMAIL_FROM_ADDR')
        msg = EmailMessage(
                self.subject,
                self._html,
                from_addr,
                self.to
                )
        msg.content_subtype = 'html'

        #msg.attach_alternative(self._html, 'text/html')
        if attach:
            msg.attach(attach['name'], attach['data'], attach['mime'])

        msg.send(fail_silently)
        return 0
