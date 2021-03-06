from rabbit_service.client import RabbitClient
from rabbit_service import rconfig
from pika.credentials import PlainCredentials

DEFAULT_MAX_LOOKUP_RESULTS = 10

TREE_INSERT = 1
TREE_DELETE = 2
TREE_LOOKUP = 3
PRINT_TREES = 4

class TreeStateClient(RabbitClient):
    def __init__(self):
        creds = PlainCredentials(rconfig.TREE_USER, rconfig.TREE_PASSWORD)
        super(TreeStateClient, self).__init__(credentials=creds, **rconfig.TREE_CLIENT_CONFIG)

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
        response = self.call(kwargs, rpc=True)
        #print response
        return response
