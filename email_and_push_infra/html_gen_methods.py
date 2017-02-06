__author__ = 'aammundi'

import signals
import pdb


# put all HTML generation code class/Method.
# there needs to be a call-in into the entry function from the handler table

class HtmlGen:
    def __init__(self, wizcard, trigger):
        self.wizcard = wizcard
        self.trigger = trigger

        self.emailHandlers = {
            # Key: (email handler, Push required)
            signals.TRIGGER_NEW_USER: (self.dummy_func, False),
            signals.TRIGGER_CONNECTION_REQUEST: (self.dummy_func, False),
            signals.TRIGGER_PENDING_INVITE: (self.dummy_func, False),
            signals.TRIGGER_CONNECTION_ACCEPTED: (self.dummy_func, False),
            signals.TRIGGER_RECOMMENDATION_AVAILABLE: (self.dummy_func, False),
        }

    def run(self):
        self.emailHandlers[self.trigger][0](self.wizcard)

    def dummy_func(self, wizcard):
        print wizcard
