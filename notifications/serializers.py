__author__ = 'aammundi'

from rest_framework import serializers
from notifications.models import Notification, BaseNotification
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
        fields = ('id', 'recipient', 'target', 'action_object', 'verb', 'delivery_method', 'do_push', 'start', 'end')

    target = GenericSerializerField()
    action_object = GenericSerializerField(required=False)
    do_push = serializers.BooleanField(required=False, default=True, write_only=True)
    start = serializers.DateTimeField(required=False, default=timezone.now(), write_only=True)
    end = serializers.DateTimeField(required=False, default=timezone.now(), write_only=True)
    delivery_method = serializers.IntegerField(required=False, default=BaseNotification.ALERT, write_only=True)

    def create(self, validated_data):
        delivery_method = validated_data.pop('delivery_method', BaseNotification.ALERT)
        start = validated_data.pop('start', timezone.now() + timedelta(minutes=1))
        end = validated_data.pop('end', timezone.now() + timedelta(minutes=1))
        do_push = validated_data.pop('do_push', False)

        push_notif = notify.send(
            self.context.get('user'),
            notif_type=verbs.WIZCARD_ENTITY_BROADCAST[0],
            do_push=do_push,
            delivery_method=delivery_method,
            start_date=start,
            end_date=end,
            fanout=True,
            **validated_data
        )

        return push_notif[0][1]



