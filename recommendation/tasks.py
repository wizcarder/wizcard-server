import json
import logging
import pika
import sys
sys.path.append("../wizcard-server")
from location_service import rconfig
from location_service.client import RabbitClient
from celery import shared_task,task
logger = logging.getLogger(__name__)



class RecoClient(RabbitClient):
    def __init__(self, *args, **kwargs):
        super(RecoClient, self).__init__(**rconfig.RECO_Q_CONFIG)

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
    recoclient = RecoClient()
    recoclient.gen_allreco(target=recotarget)

@task(ignore_result=True)
def triggerRecoAll():
    recoclient = RecoClient()
    recoclient.gen_allreco(target='full')


