#!/usr/bin/env python

import sys
sys.path.append("../wizcard-server")
sys.path.append("../wizcard-server/lib")

from lib.pytrie import SortedStringTrie as trie
from lib import wizlib
import pika
import uuid
import heapq
#from base.borg import Borg
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

class LocationServiceClient(object):

    basic_connection = None

    def __init__(self, *args, **kwargs):
        #Borg.__init__(self)
        self.host = kwargs.get('host', rconfig.HOST)
        self.exchange = kwargs.get('exchange', rconfig.EXCHANGE)
        self.routing_key = kwargs.get('routing_key', rconfig.ROUTING_KEY)
        self.rpc_connection = None
        self.channel = None
        self.response = None

    def connection_setup(self):
        return pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host))


    def call(self, params, rpc=False):
        if rpc:
            self.rpc_connection = self.connection_setup()
            self.channel = self.rpc_connection.channel()
            result = self.channel.queue_declare(exclusive=True)
            self.corr_id = str(uuid.uuid4())
            callback_queue = result.method.queue
            self.channel.basic_consume(self.on_response, no_ack=True,
                    queue=callback_queue)

            params['rpc'] = True
            self.channel.basic_publish(exchange=self.exchange,
                    routing_key=self.routing_key,
                    properties=pika.BasicProperties(
                        reply_to = callback_queue,
                        correlation_id = self.corr_id,
                        ),
                    body=json.dumps(params))

            self.channel.start_consuming()
            self.rpc_connection.close()
        else:
            if not LocationServiceClient.basic_connection:
                LocationServiceClient.basic_connection = self.connection_setup()
            try:
                self.channel = LocationServiceClient.basic_connection.channel()
            except:
                LocationServiceClient.basic_connection = self.connection_setup()
                self.channel = LocationServiceClient.basic_connection.channel()

            self.channel.basic_publish(exchange=self.exchange,
                                       routing_key=self.routing_key,
                                       body=json.dumps(params))

        if self.response:
            return json.loads(self.response)
        return None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body
            self.channel.stop_consuming()

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
        response = self.call(kwargs, rpc=True)
        return response['result'], response['count']

    def print_trees(self, **kwargs):
        kwargs['fn'] = PRINT_TREES
        response = self.call(kwargs)
        return response
