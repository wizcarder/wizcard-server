import sys
sys.path.append(".")
import os
from wizcard import instances
RUNENV=os.getenv("WIZRUNENV", "dev")
EXCHANGE = 'trees'
EXCHANGE_TYPE = 'direct'
QUEUE = 'treeQ'
ROUTING_KEY = 'location_service'
HOST = instances.ALLHOSTS[RUNENV]['LOCATIONSERVER'][0]

