#!/usr/bin/env python

import sys
import os
import pika
import uuid
from rabbit_service import rconfig
import json
import logging
from wizcard.instances import ALLHOSTS

RPC_CONN = 1
BASIC_CONN = 2

logger = logging.getLogger(__name__)
RUNENV = os.getenv("WIZRUNENV", "dev")


class RabbitClient(object):
    def __init__(self, *args, **kwargs):
        self.host = kwargs.get('host', ALLHOSTS[RUNENV]['RABBITSERVER'][0])
        self.virtual_host = kwargs.get('virtual_host', "")
        self.credentials = kwargs.get('credentials', None)
        self.exchange = kwargs.get('exchange', rconfig.DEFAULT_EXCHANGE)
        self.routing_key = kwargs.get('routing_key', rconfig.DEFAULT_ROUTING_KEY)
        self.connection = None
        self.type = BASIC_CONN
        self.channel = None
        self.response = None

    def connection_setup(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.host,
                virtual_host=self.virtual_host,
                credentials=self.credentials
            )
        )

    def connection_close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def call(self, params, rpc=False):
        self.connection_setup()
        self.channel = self.connection.channel()
        if rpc:
            result = self.channel.queue_declare(exclusive=True)
            self.corr_id = str(uuid.uuid4())
            callback_queue = result.method.queue
            self.channel.basic_consume(self.on_response, no_ack=True,
                                       queue=callback_queue)

            params['rpc'] = True
            self.channel.basic_publish(exchange=self.exchange,
                                       routing_key=self.routing_key,
                                       properties=pika.BasicProperties(
                                           reply_to=callback_queue,
                                           correlation_id=self.corr_id,
                                       ),
                                       body=json.dumps(params))

            self.channel.start_consuming()
        else:
            self.channel.basic_publish(exchange=self.exchange,
                                       routing_key=self.routing_key,
                                       body=json.dumps(params))

        if self.response:
            return json.loads(self.response)
        self.connection_close()
        return None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body
            self.channel.stop_consuming()



