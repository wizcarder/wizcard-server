import json
import logging
import pika
from celery import shared_task,task
logger = logging.getLogger(__name__)

@task(ignore_result=True)
def triggerRecoAll():
    addtoQtask.delay('recoall','all','all')


@shared_task
def addtoQtask(recqueue,recotarget,recmodel):

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=recqueue)

    body_dict = {'recotarget' : str(recotarget), 'recmodel': recmodel}
    body_data = json.dumps(body_dict)


    channel.basic_publish(exchange='',
                          routing_key=recqueue,
                          body=body_data)
    logger.info("Sending %s to Q", recotarget)
    connection.close()

