import sys
sys.path.append(".")
import os
from wizcard import instances

RUNENV=os.getenv("WIZRUNENV", "dev")

# AMPQ Settings
HOST = 'localhost' 
RECO_PROTOCOL = 'amqp://'
RECO_PORT = 5672
RECO_HOST = 'localhost'
RECO_USER = 'reco_user'
RECO_PASS = 'reco_pass'


# URLS
AMPQ_RECO_URL = RECO_PROTOCOL + RECO_USER + ':' + RECO_PASS + '@' + RECO_HOST + ':5672'  


#EXchange default settings
EXCHANGE_TYPE = 'direct'
RECO_TRIGGER_Q = 'reco_triggerq'
RECO_PERIODIC_Q = 'reco_periodicq'
RECO_TRIGGER_KEY = 'reco_trigger_key'
RECO_PERIODIC_KEY = 'reco_periodic_key'

RECO_TRIGGER_CONFIG = {
    'url' : AMPQ_RECO_URL,
    'exchange' : 'reco',
    'queue': RECO_TRIGGER_Q,
    'routing_key': RECO_TRIGGER_KEY,
}
RECO_PERIODIC_CONFIG = {
    'url' : AMPQ_RECO_URL,
    'exchange' : 'reco',
    'queue': RECO_PERIODIC_Q,
    'routing_key': RECO_PERIODIC_KEY,
}
