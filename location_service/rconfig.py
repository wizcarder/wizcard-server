import sys
sys.path.append(".")
import os
from wizcard import instances

RUNENV=os.getenv("WIZRUNENV", "dev")

# AMPQ Settings
HOST =  instances.ALLHOSTS[RUNENV]['RABBITSERVER'][0]
BROKER_TRANSPORT = 'amqp'
BROKER_USER = 'wizcard_user'
BROKER_PASSWORD = 'wizcard_pass'
TREE_USER = 'location_user'
TREE_PASSWORD = 'location_pass'
BROKER_HOST = 'localhost'
BROKER_PORT = 5672
BROKER_VHOST = 'wizcard_vhost'


# URLS
AMPQ_DEFAULT_URL = 'amqp://' + BROKER_USER + ':' + BROKER_PASSWORD + '@'+ BROKER_HOST +':5672' + '/' + BROKER_VHOST
AMPQ_TREE_URL = 'amqp://' + TREE_USER + ':' + TREE_PASSWORD + '@'+ BROKER_HOST +':5672'


#EXchange default settings
EXCHANGE_TYPE = 'direct'
DEFAULT_EXCHANGE = ''
DEFAULT_QUEUE = 'default'
DEFAULT_ROUTING_KEY = 'default'

# consumer/prod specific settings
TREE_SERVER_Q_NAME = 'treeQ'
TREE_SERVER_ROUTING_KEY = 'location_service'

RECO_Q_NAME = 'recoQ'
RECO_ROUTING_KEY = 'reco_key'

TREE_SERVER_CONFIG = {
    'url' : AMPQ_TREE_URL,
    'exchange' : 'trees',
    'queue': TREE_SERVER_Q_NAME,
    'routing_key': TREE_SERVER_ROUTING_KEY,
}

RECO_Q_CONFIG = {
    'url' : AMPQ_DEFAULT_URL,
    'exchange' : 'reco',
    'queue': RECO_Q_NAME,
    'routing_key': RECO_ROUTING_KEY,
}
