import logging

from celery import task

from entity.models import Event
from entity.models import Campaign
from entity.serializers import CampaignSerializer
from wizcard.settings import feed_schemas
from base_entity.models import BaseEntityComponent
import pdb


logger = logging.getLogger(__name__)


@task(ignore_result=True)
def expire():
    logger.debug('Event Tick received')
    e = Event.objects.get_expired()
    for _e in e:
        logger.info('Expiring event {%s}', _e)
        _e.do_expire()


def create_entities(file, entity_type, owner):
    record_no = 0
    problematic_records = []
    cls, ser = BaseEntityComponent.entity_cls_ser_from_type(entity_type, create=True)

    schema = feed_schemas[entity_type]
    schema_fields_len = len(schema)


    for line in file:
        # CLeanup and validations
        line = line.rstrip()

        # Skip empty lines
        if not line:
            continue

        record_no += 1
        ser_data = dict()
        arr = line.split('\t')

        # If arr has less fields than what schema needs then flag it
        if len(arr) < schema_fields_len:
            problematic_records.append(str(record_no))
            continue

        for i in range(0, schema_fields_len):
            ser_data[schema[i]] = arr[i]

        # Ideally we can do many=True but we also want to point out faulty records

        s = ser(data=ser_data, context={'user':owner})
        if s.is_valid():
            s.save()
        else:
            problematic_records.append(str(record_no))

    success_records = record_no - len(problematic_records)

    return (success_records, ','.join(problematic_records))



