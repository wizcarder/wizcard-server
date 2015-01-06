#!/usr/bin/env python

import sys
sys.path.append("../wizcard-server")
sys.path.append("../wizcard-server/lib")

from lib.pytrie import SortedStringTrie as trie
from lib import wizlib
from server import LocationServiceServer
import pika
import uuid
import heapq
import json
import logging
import rconfig
import pdb

DEFAULT_MAX_LOOKUP_RESULTS = 10

TREE_INSERT = 1
TREE_DELETE = 2
TREE_LOOKUP = 3
PRINT_TREES = 4

logger = logging.getLogger(__name__)

class TreeServer(LocationServiceServer):

    def __init__(self, *args, **kwargs):

        super(TreeServer, self).__init__(*args, **kwargs)
        self.ptree = trie()
        self.vtree = trie()
        self.wtree = trie()
        
        self.location_tree_handles = {
            "PTREE" : self.ptree,
            "WTREE" : self.wtree,
            "VTREE" : self.vtree
        }

        self.call_handles = {
            TREE_INSERT : self.tree_insert,
            TREE_DELETE : self.tree_delete,
            TREE_LOOKUP : self.lookup,
            PRINT_TREES : self.print_trees
        }
        
        self.server_running = False

    def on_message(self, ch, basic_deliver, props, body):
        logger.info('Received message # %s from %s: %s',
                     basic_deliver.delivery_tag, props.app_id, body)
        args = json.loads(body)
        fn = args.pop('fn')
        response = self.call_handles[fn](**args)

        ch.basic_publish(exchange="",
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                         body=json.dumps(response))

        self.acknowledge_message(basic_deliver.delivery_tag)

    def get_tree_from_type(self, tree_type):
	return self.location_tree_handles[tree_type]

    def tree_insert(self, **kwargs):
        tree_type = kwargs.pop('tree_type')
        key = kwargs.pop('key')
        val = kwargs.pop('val')

        tree = self.get_tree_from_type(tree_type)
        val = self.t_ins(tree, key, val)

        result = dict()
        result['result'] =  val
        return result

    def t_ins(self, tree, key, val):
        tree[key] = val
        return val

    def tree_delete(self, **kwargs):
        tree_type = kwargs.pop('tree_type')
        key = kwargs.pop('key')

        tree = self.get_tree_from_type(tree_type)
        val = self.t_del(tree, key)
        result = dict()
        result['result'] =  val
        return result

    def t_del(self, tree, key):
        val = None
        try:
            val = tree[key]
            del tree[key]
        except:
            pass
        return val

    def lookup(self, **kwargs):
        tree_type = kwargs.pop('tree_type')
        key = kwargs.pop('key')
        exclude_key = kwargs.pop('exclude_key', True)
        n = kwargs.pop('n', DEFAULT_MAX_LOOKUP_RESULTS)

	tree = self.get_tree_from_type(tree_type)
        if exclude_key:
            cached_val = self.t_del(tree, key)

        ret, count = self.lookup_closest_n(tree, key, n)

        if exclude_key:
            self.t_ins(tree, key, cached_val)

        logger.debug('looking up gives [%d] result [%s]', count, ret)

        result = dict()
        result['result'] = ret
        result['count'] = count
        return result

    def print_trees(self, **kwargs):
        tree_type = kwargs.pop('tree_type', None)
        result = dict()
	if tree_type == None:
            for ttype in self.location_tree_handles:
                tree = self.get_tree_from_type(ttype)
                print '{ttype} : {tree}'.format (ttype=ttype, tree=tree)
                result[ttype] = dict(tree)
	else:
            tree = self.get_tree_from_type(tree_type)
            print '{ttype} : {tree}'.format (ttype=tree_type, tree=tree)
            result[tree_type] = dict(tree)

        return result

    def lookup_closest_n(self, tree, key, n):
        #lookup using top half of key
        result = None
        count = 0
        left = 0
        right = len(key)
        part = right
        done = False

        while not done:
            part = ((right + left - 1)//2) + 1
            result, count = tree.longest_common_prefix_value(key[:part])
            if part == right:
                done = True

            prev_result = result
            prev_count = count

            if count < n:
                right = part
            elif count > n:
                left = part
            else:
                break
                
        #one result is over and one is under. take the larger one
        return (result, count) if count > prev_count else (prev_result, prev_count)

def main():
    logging.basicConfig(level=logging.INFO)
    ts = TreeServer('amqp://guest:guest@localhost:5672/%2F')
    try:
        ts.run()
    except KeyboardInterrupt:
        ts.stop()

if __name__ == '__main__':
    main()
