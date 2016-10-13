#!/usr/bin/env python
import sys
import pdb

sys.path.append(".")

from lib.pytrie import SortedStringTrie as trie
from lib import wizlib
#from base.db import WizcardDB
from base.db import WizcardDB
from server import RabbitServer
from wizcard import settings
import rconfig
import pika

import json
import logging


DEFAULT_MAX_LOOKUP_RESULTS = 10

FORMAT= '[%(levelname)s] %(asctime)s - M:%(module)s, P:%(process)d, T:%(thread)d, MSG:%(message)s'

TREE_INSERT = 1
TREE_DELETE = 2
TREE_LOOKUP = 3
PRINT_TREES = 4

if settings.DEBUG:
    logging.basicConfig(format=FORMAT,level=logging.DEBUG)
else:
    logging.basicConfig(fileneme="./log/location_server.log",format=FORMAT,level=logging.INFO)

logger = logging.getLogger(__name__)

class TreeServer(RabbitServer):

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

        #init trees reading from db outside of django
        logger.info('initing trees from db')

        sdict = settings.DATABASES['default']
        logger.info('initing trees from %s, %s',sdict['HOST'])

        wdb = WizcardDB(
                socket=sdict['HOST'],
                user=sdict['USER'],
                passwd=sdict['PASSWORD'],
                db=sdict['NAME']
        )

        wdb.table_select('select * from location_mgr_locationmgr')
        for row in wdb.ResultIter():
                pk = row[0]
                key = row[3]
                tree_type = row[4]
                #modified key for tree ins
                logger.info('inserting [%s, %s] into (%s)', key, pk, tree_type)
                self.t_ins(
                        self.get_tree_from_type(tree_type),
                        wizlib.modified_key(key, pk),
                        pk)

        wdb.close()

    def on_message(self, ch, basic_deliver, props, body):
        logger.info('Received message # %s from %s: %s',
                     basic_deliver.delivery_tag, props.app_id, body)
        args = json.loads(body)
        fn = args.pop('fn')
        rpc = args.pop('rpc', False)
        response = self.call_handles[fn](**args)


        if rpc:
            logger.info('Received RPC:%s type %s, response: %s', rpc, fn, response)
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

        logger.debug('tree insert {0}: {1}:{2}'.format(tree_type, key, val))
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
        logger.debug('tree delete {0}: {1}:{2}'.format(tree_type, key, val))
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
        exclude_self = kwargs.pop('exclude_self', True)
        n = kwargs.pop('n', DEFAULT_MAX_LOOKUP_RESULTS)

        tree = self.get_tree_from_type(tree_type)
        if exclude_self:
            cached_val = self.t_del(tree, key)

        ret, count = self.lookup_closest_n(tree, key, n)

        if exclude_self and cached_val:
            self.t_ins(tree, key, cached_val)

        logger.debug('looking up gives [%d] result [%s]', count, ret)
        logger.debug('tree lookup {0}: {1}:{2}'.format(tree_type, key, ret))

        result = dict()
        result['result'] = ret
        result['count'] = count
        return result

    def print_trees(self, **kwargs):
        tree_type = kwargs.pop('tree_type', None)
        result = dict()
        print 'Tree State'
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


import daemon
def main():
    logging.basicConfig(level=logging.INFO)
    isdaemon = False
    for params in sys.argv:
        if params == '--D' or params == '-daemon':
            isdaemon = True

    ts = TreeServer(**rconfig.TREE_SERVER_CONFIG)

    if isdaemon:
        with daemon.DaemonContext():
            ts.run()
    else:
        try:
            ts.run()
        except KeyboardInterrupt:
            ts.stop()

if __name__ == '__main__':
    main()
