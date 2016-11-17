from wizcard.instances  import *
import os

RUNENV = os.getenv('WIZRUNENV', 'dev')
# AMPQ Settings
BROKER_TRANSPORT = 'amqp'
BROKER_HOST = 'localhost'
BROKER_PORT = 5672

BROKER_VHOST = 'wizcard_vhost'
BROKER_USER = 'wizcard_user'
BROKER_PASSWORD = 'wizcard_pass'


TREE_VHOST = 'location_vhost'
TREE_USER = 'location_user'
TREE_PASSWORD = 'location_pass'

RECO_VHOST = 'reco_vhost'
RECO_USER = 'reco_user'
RECO_PASSWORD = 'reco_pass'



# URLS
TREE_HOST =  RUNHOSTS[RUNENV]['LOCATIONSERVER'][0]
AMPQ_DEFAULT_URL = 'amqp://' + BROKER_USER + ':' + BROKER_PASSWORD + '@'+ BROKER_HOST +':5672' + '/' + BROKER_VHOST
AMPQ_TREE_URL = 'amqp://' + TREE_USER + ':' + TREE_PASSWORD + '@'+ TREE_HOST +':5672'
AMPQ_RECO_URL = 'amqp://' + RECO_USER + ':' + RECO_PASSWORD + '@'+ BROKER_HOST +':5672'


#EXchange default settings
EXCHANGE_TYPE = 'direct'
DEFAULT_EXCHANGE = ''
DEFAULT_QUEUE = 'default'
DEFAULT_ROUTING_KEY = 'default'

# consumer/prod specific settings
TREE_SERVER_Q_NAME = 'treeQ'
TREE_SERVER_ROUTING_KEY = 'location_service'


RECO_TRIGGER_Q_NAME = 'reco_triggerq'
RECO_TRIGGER_ROUTING_KEY = 'reco_trigger_key'

RECO_PERIODIC_Q_NAME = 'reco_periodicq'
RECO_PERIODIC_ROUTING_KEY = 'reco_periodic_key'

TREE_SERVER_CONFIG = {
    'virtual_host': TREE_VHOST,
    'url' : AMPQ_TREE_URL,
    'exchange' : 'trees',
    'queue': TREE_SERVER_Q_NAME,
    'routing_key': TREE_SERVER_ROUTING_KEY,
}

RECO_TRIGGER_CONFIG = {
    'virtual_host': RECO_VHOST,
    'url' : AMPQ_RECO_URL,
    'exchange' : 'reco',
    'queue': RECO_TRIGGER_Q_NAME,
    'routing_key': RECO_TRIGGER_ROUTING_KEY,
}

RECO_PERIODIC_CONFIG = {
    'virtual_host': RECO_VHOST,
    'url' : AMPQ_RECO_URL,
    'exchange' : 'reco',
    'queue': RECO_PERIODIC_Q_NAME,
    'routing_key': RECO_PERIODIC_ROUTING_KEY,
}




