__author__ = 'aammundi'

from models import EmailAndPush, EmailEvent
from lib.create_share import send_wizcard, send_event
import pdb


# put all HTML generation code class/Method.
# there needs to be a call-in into the entry function from the handler table

class HtmlGen:
    def __init__(self, sender, trigger, to):
        self.sender = sender
        self.trigger = trigger
        self.to = to

        self.emailHandlers = {
            # Key: (email handler, Push required)
            EmailEvent.NEWUSER: (self.welcome_user, False),
            EmailEvent.INVITED: (self.invite_user, False),
            EmailEvent.NEWRECOMMENDATION: (self.dummy_func, False),
            EmailEvent.SCANNED: (self.scan_user, False),
            EmailEvent.INVITE_EXHIBITOR: (self.invite_exhibitor, False)
        }

    def run(self):
        self.emailHandlers[self.trigger][0](self.sender, self.to)

    def dummy_func(self, sender):
        object = sender.get()
        print object

    def welcome_user(self, sender, to):
        wizcard = sender
        email_details = {"template" : "welcome.html", "subject": "Welcome %s to WizCard"}
        send_wizcard.delay(wizcard, to, email_details, half_card=True)

    def invite_user(self, sender, to):
        wizcard = sender
        email_details = {"template": "emailwizcard.html", "subject": "%s has invited you to Connect on WizCard"}
        send_wizcard.delay(wizcard, to,  email_details)

    def scan_user(self, sender, to):
        wizcard = sender.get()
        email_details = {"template" : "emailwizcard.html", "subject": "%s has Scanned your Card on WizCard"}
        send_wizcard.delay(wizcard, to, email_details, half_card = True)


    def invite_exhibitor(self, sender, to):
        event_organizer = sender
        event_image = sender.get_banner()

        email_details = {"template" : "invite_exhibitor.html", "subject": "%s - has invited you to Create your Product", "from_addr": event_organizer.creator.email}
        send_event(event_organizer, to, email_details)






