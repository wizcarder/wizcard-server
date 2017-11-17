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
        fields = ('id', 'delivery_type', 'recipient', 'target', 'action_object', 'verb',
                  'start', 'end', 'notif_type', 'do_push')

    target = GenericSerializerField()
    action_object = GenericSerializerField(required=False)
    start = serializers.DateTimeField(required=False)
    end = serializers.DateTimeField(required=False)
    # AA Comments: notif_type needn't really be exposed in rest. Leaving it here for now.
    notif_type = serializers.IntegerField(required=False, default=verbs.WIZCARD_ENTITY_BROADCAST_CREATE[0])
    do_push = serializers.BooleanField(required=False, default=True, write_only=True)

    def create(self, validated_data):
        delivery_type = validated_data.pop('delivery_type', Notification.ALERT)
        start = validated_data.pop('start', timezone.now() + timedelta(minutes=1))
        end = validated_data.pop('end', timezone.now() + timedelta(minutes=1))
        do_push=validated_data.pop('do_push', False)

        # AA: Comments: this was broken
        push_notif = notify.send(
            self.context.get('user'),
            do_push=do_push,
            is_async=True,
            delivery_type=delivery_type,
            start_date=start,
            end_date=end,
            **validated_data
        )

        return push_notif[0][1]