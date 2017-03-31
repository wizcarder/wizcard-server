__author__ = 'aammundi'

from models import EmailAndPush, EmailEvent
from lib.create_share import send_wizcard
import pdb


# put all HTML generation code class/Method.
# there needs to be a call-in into the entry function from the handler table

class HtmlGen:
    def __init__(self, wizcard, trigger, to):
        self.wizcard = wizcard
        self.trigger = trigger
        self.to = to

        self.emailHandlers = {
            # Key: (email handler, Push required)
            EmailEvent.NEWUSER: (self.welcome_user, False),
            EmailEvent.INVITED: (self.invite_user, False),
            EmailEvent.NEWRECOMMENDATION: (self.dummy_func, False),
            EmailEvent.SCANNED: (self.scan_user, False)
        }

    def run(self):
        self.emailHandlers[self.trigger][0](self.wizcard, self.to)

    def dummy_func(self, wizcard):
        print wizcard

    def welcome_user(self, wizcard, to):
        email_details = {"template" : "welcome.html", "subject": "Welcome %s to WizCard"}
        send_wizcard.delay(wizcard, to, email_details, half_card=True)

    def invite_user(self, wizcard, to):
        email_details = {"template": "emailwizcard.html", "subject": "%s has invited you to Connect on WizCard"}
        send_wizcard.delay(wizcard, to,  email_details)

    def scan_user(self, wizcard, to):
        email_details = {"template" : "emailwizcard.html", "subject": "%s has Scanned your Card on WizCard"}
        send_wizcard.delay(wizcard, to, email_details, half_card = True)





