#!/usr/bin/env python

import sys
sys.path.append("../wizcard-server")
sys.path.append("../wizcard-server/lib")

from lib.pytrie import SortedStringTrie as trie
from lib import wizlib
from lib.borg import Borg
import pika
import uuid
import heapq
import rconfig
import json
import logging
import pdb

DEFAULT_MAX_LOOKUP_RESULTS = 10

TREE_INSERT = 1
TREE_DELETE = 2
TREE_LOOKUP = 3
PRINT_TREES = 4

logger = logging.getLogger(__name__)

class LocationServiceClient(Borg):

    connection_created = False
    reconnected_count = 0

    def __init__(self, *args, **kwargs):
        Borg.__init__(self)

    def connection_setup(self):
        #init rabbitmq client side connection
        if not self.connection_created:
            self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters( host='localhost'))

            self.channel = self.connection.channel()
            result = self.channel.queue_declare(exclusive=True)
            self.callback_queue = result.method.queue
            self.channel.basic_consume(self.on_response, no_ack=True,
                                       queue=self.callback_queue)
            self.connection_created = True

    def call(self, params):
        if not self.connection_created:
            self.connection_setup()

        self.response = None
        self.corr_id = str(uuid.uuid4())
        try:
            self.channel.basic_publish(exchange=rconfig.EXCHANGE,
                    routing_key=rconfig.ROUTING_KEY,
                    properties=pika.BasicProperties(
                        reply_to = self.callback_queue,
                        correlation_id = self.corr_id,
                        ),
                    body=json.dumps(params))
        except:
            logger.error('pika rabbitmq connection dropped')
            self.connection_created = False
            self.connection_setup()
            self.reconnected_count += 1

        while self.response is None:
            self.connection.process_data_events()
        return json.loads(self.response)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body
            print " [.] Got %r" % (self.response,)

    def tree_insert(self, **kwargs):
        kwargs['fn'] = TREE_INSERT
        response = self.call(kwargs)
        return response

    def tree_delete(self, **kwargs):
        kwargs['fn'] = TREE_DELETE
        response = self.call(kwargs)
        return response

    def lookup(self, **kwargs):
        kwargs['fn'] = TREE_LOOKUP
        response = self.call(kwargs)
        return response['result'], response['count']

    def print_trees(self, **kwargs):
        kwargs['fn'] = PRINT_TREES
        response = self.call(kwargs)
        return response
