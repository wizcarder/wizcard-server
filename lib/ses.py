from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template  import Template,Context
from django.template.loader import render_to_string
import pdb
import logging

logger = logging.getLogger(__name__)

class Email(object):
    
    def __init__(self, to, subject):
        self.to = to
        self.subject = subject
        self._html = None
        self._text = None

    def _render(self, emailtemplate, context):
        return render_to_string(emailtemplate,context)

    def html(self, emailtemplate, context):
        self._html = self._render(emailtemplate, context)

    def text(self, emailtemplate, context):
        self._text = self._render(emailtemplate, context)

    def send(self, from_addr=None, fail_silently=False):
        if isinstance(self.to, basestring):
            self.to = [self.to]
        if not from_addr:
            from_addr = getattr(settings, 'EMAIL_FROM_ADDR')
        msg = EmailMultiAlternatives(
                self.subject,
                self._text,
                from_addr,
                self.to
                )
        if self._html:
            msg.attach_alternative(self._html, 'text/html')
        msg.send(fail_silently)
