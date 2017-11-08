__author__ = 'aammundi'

from rest_framework import serializers
from notifications.models import Notification
from notifications.signals import notify
from rest_framework.validators import ValidationError
from django.contrib.contenttypes.models import ContentType
from wizserver import verbs
from django.utils import timezone
from datetime import timedelta


import pdb

class GenericSerializerField(serializers.RelatedField):

    def get_queryset(self):
        pass

    def to_internal_value(self, data):
        id = data.get('id', None)
        type = data.get('type', None)

        # Perform the data validation.
        if id is None:
            raise ValidationError({
                'id': 'This field is required.'
            })
        if not type:
            raise ValidationError({
                'type': 'This field is required.'
            })

        ct = ContentType.objects.get(model=type)
        obj = ct.get_object_for_this_type(id=id)
        return obj


    def to_representation(self, value):
        return dict(
            type=ContentType.objects.get_for_model(value).name,
            id=value.pk
        )


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'delivery_type', 'recipient', 'actor', 'target', 'action_object', 'verb',
                  'start', 'end', 'notif_type')


    actor = GenericSerializerField()
    recipient = GenericSerializerField()
    target = GenericSerializerField()
    action_object = GenericSerializerField(required=False)
    start = serializers.DateTimeField(required=False)
    end = serializers.DateTimeField(required=False)
    notif_type = serializers.IntegerField(required=False)

    def create(self, validated_data):
        parms = dict()

        actor = validated_data.pop('actor')
        recipient = validated_data.pop('recipient')
        notif_type = validated_data.pop('notif_type', verbs.WIZCARD_EVENT_BROADCAST[0])
        delivery_type = validated_data.pop('delivery_type', Notification.ALERT)
        start = validated_data.pop('start', timezone.now() + timedelta(minutes=1))
        end = validated_data.pop('end', timezone.now() + timedelta(minutes=1))


        target = validated_data.pop('target', None)
        parms.update(target=target)
        parms.update(verb=validated_data.pop('verb'))


        action_object = validated_data.pop('action_object', None)
        parms.update(action_object=action_object)

        push_notif = notify.send(actor,
                                 recipient=recipient,
                                 notif_type=notif_type,
                                 delivery_type=delivery_type,
                                 start_date=start,
                                 end_date=end,
                                 **parms
                                 )

        return push_notif[0][1]


