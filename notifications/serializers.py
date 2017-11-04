__author__ = 'aammundi'

from rest_framework import serializers
from notifications.models import Notification
from rest_framework.validators import ValidationError
from django.contrib.contenttypes.models import ContentType


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

        return {
            'id': id,
            'type': type
        }

    def to_representation(self, value):
        return dict(
            type=ContentType.objects.get_for_model(value).name,
            id=value.pk
        )


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'delivery_type', 'recipient', 'actor', 'target', 'action_object', 'verb',
                  'start', 'end')

    actor = GenericSerializerField(required=True)
    target = GenericSerializerField()
    action_object = GenericSerializerField()
    start = serializers.DateTimeField(required=False)
    end = serializers.DateTimeField(required=False)

    def create(self, validated_data):
        parms = dict()

        actor = validated_data.pop('actor')
        parms.update(actor_content_type=ContentType.objects.get(model=actor['type']))
        parms.update(actor_object_id=actor['id'])

        target = validated_data.pop('target', None)
        if target:
            parms.update(target_content_type=ContentType.objects.get(model=target['type']))
            parms.update(target_object_id=target['id'])

        action_object = validated_data.pop('action_object', None)
        if action_object:
            parms.update(action_object_content_type=ContentType.objects.get(model=action_object['type']))
            parms.update(action_object_object_id=action_object['id'])

        n = Notification.objects.create(
            delivery_type=validated_data['delivery_type'],
            is_async=True,
            recipient=validated_data['recipient'],
            verb=validated_data['verb'],
            **parms
        )

        return n


