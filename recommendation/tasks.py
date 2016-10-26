import logging
import sys

#from rabbit_service import rconfig
from rabbit_service.client import RabbitClient, rconfig
from celery import shared_task, task
from pika.credentials import PlainCredentials
import pdb
logger = logging.getLogger(__name__)


class RecoClient(RabbitClient):
    def __init__(self, *args, **kwargs):
        creds = PlainCredentials(rconfig.RECO_USER, rconfig.RECO_PASSWORD)
        super(RecoClient, self).__init__(credentials=creds, **kwargs)

    def gen_allreco(self, **kwargs):
        kwargs['fn'] = 2 
        response = self.call(kwargs)
        return response

    def gen_abreco(self, **kwargs):
        kwargs['fn'] = 0
        response = self.call(kwargs)
        return response

    def gen_wizreco(self, **kwargs):
        kwargs['fn'] = 1
        response = self.call(kwargs)
        return response


def addtoQtask(recotarget):
    recoclient = RecoClient(**rconfig.RECO_TRIGGER_CONFIG)
    recoclient.gen_allreco(target=recotarget)


@task(ignore_result=True)
def triggerRecoAll():
    recoclient = RecoClient(**rconfig.RECO_PERIODIC_CONFIG)
    recoclient.gen_allreco(target='full')


