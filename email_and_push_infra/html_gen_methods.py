__author__ = 'aammundi'

from models import EmailAndPush
from lib.create_share import send_wizcard, send_event
from wizserver import verbs
import pdb


# put all HTML generation code class/Method.
# there needs to be a call-in into the entry function from the handler table

class HtmlGen:
    def __init__(self, sender, trigger, target):
        self.sender = sender
        self.trigger = trigger
        self.target = target 

        self.emailHandlers = {
            # Key: (email handler, Push required)
            verbs.WIZCARD_NEW_USER[0]: (self.welcome_user, False),
            verbs.WIZCARD_INVITE_USER[0]: (self.invite_user, False),
            verbs.WIZCARD_SCANNED_USER[0]: (self.scan_user, False),
#            EmailEvent.NEWRECOMMENDATION: (self.dummy_func, False),
#            EmailEvent.SCANNED: (self.scan_user, False),
#            EmailEvent.INVITE_EXHIBITOR: (self.invite_exhibitor, False),
#            EmailEvent.INVITE_ATTENDEE: (self.invite_attendee, False)
        }

        #self.notifHandlers = {
        #    verbs.WIZCARD_MESG_ATTENDEE[0]: (self.mesg_attendees, False)
        #}

    def email_send(self):
        self.emailHandlers[self.trigger][0](self.sender, self.target)

    def notif_send(self):
        self.notifHandlers[self.trigger][0](self.sender, self.target)

    def dummy_func(self, sender):
        object = sender.get()
        print object

    def welcome_user(self, sender, target):
        wizcard = target
        try:
            to = target.get_email
        except:
            return -1
        email_details = {"template" : "welcome.html", "subject": "Welcome %s to WizCard"}
        send_wizcard(wizcard, to, email_details, half_card=True)
        return 0

    def invite_user(self, sender, target):
        wizcard = sender.wizcard
        try:
            to = target.get_email
        except:
            return -1
        email_details = {"template": "emailwizcard.html", "subject": "%s has invited you to Connect on WizCard"}
        send_wizcard(wizcard, to,  email_details)
        return 0

    def scan_user(self, sender, target):
        wizcard = sender.wizcard
        try:
            to = target.get_email
        except:
            return -1
        email_details = {"template": "emailwizcard.html", "subject": "%s has Scanned your Card on WizCard"}
        send_wizcard(wizcard, to, email_details, half_card = True)
        return 0

    def invite_exhibitor(self, sender, target):
        event_organizer = sender
        email_details = {"template": "invite_exhibitor.html", "subject": "%s - has invited you to Create your Campaign"}
        send_event(event_organizer, to, email_details)
        return 0

    def invite_attendee(self, sender, target):
        event_organizer = sender
        email_details = {"template" : "invite_attendee.html", "subject": "%s - Welcome to %s"}
        send_event(event_organizer, to, email_details)
        return 0








