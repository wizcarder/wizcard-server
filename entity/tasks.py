import logging

from celery import task

from entity.models import Event
from entity.models import Campaign
from entity.serializers import CampaignSerializer
from wizserver.verbs import feed_schemas, FEED_SEPERATOR
from base_entity.models import BaseEntityComponent
from entity.serializers import TaganomySerializer
import pdb


logger = logging.getLogger(__name__)


@task(ignore_result=True)
def expire():
    logger.debug('Event Tick received')
    e = Event.objects.get_expired()
    for _e in e:
        logger.info('Expiring event {%s}', _e)
        _e.do_expire()


def create_entities(file, owner, **kwargs):
    record_no = 0
    problematic_records = []
    event_id = kwargs.get('event')
    entity_type = kwargs.get('type')
    cls, ser = BaseEntityComponent.entity_cls_ser_from_type_and_level(
        entity_type,
        level=BaseEntityComponent.SERIALIZER_FULL
    )
    temp_tags = []
    taglist = []

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
        arr = line.split(FEED_SEPERATOR)

        #If arr has less fields than what schema needs then flag it
        if len(arr) < schema_fields_len:
            problematic_records.append(str(record_no))
            continue

        existing_entities = cls.objects.owners_entities(owner)

        for i in range(0, schema_fields_len):
            ser_data[schema[i]] = arr[i]
            inst = cls.objects.get_existing_entity(ser_data['name'], ser_data['email'], owner)

        temp_tags = ser_data.pop('tags', []).split(',')
        taglist = taglist + temp_tags
        venue = ser_data.pop('venue', "")

        if inst:
            ser(inst, data=ser_data, context={'user': owner}, partial=True)
        else:
         # Ideally we can do many=True but we also want to point out faulty records
            ser(data=ser_data, context={'user': owner})
        if ser.is_valid():
            inst = ser.save()
            if event_id:
                event = Event.objects.get(id=event_id)
                event.add_subentity_obj(inst,
                                        alias=BaseEntityComponent.sub_entity_type_from_entity_type(cls, entity_type),
                                        join_fields={'venue': venue}
                                        )
                inst.tags.set(temp_tags)

        else:
            problematic_records.append(str(record_no))

    if event_id:
        event = Event.objects.get(id=event_id)

        taganomy = event.get_subentities_of_type(BaseEntityComponent.SUB_ENTITY_CATEGORY)
        if taganomy:
            taganomy.tags.add(taglist)
        else:
            ser = TaganomySerializer(data = {"name": event.name + "_Tags", "tags": taglist}, context={'user': owner})
            if ser.is_valid():
                inst = ser.save()
                event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_CATEGORY)
            else:
                problematic_records.append(str(record_no))


    success_records = record_no - len(problematic_records)

    return (success_records, ','.join(problematic_records))



