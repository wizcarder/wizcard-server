__author__ = 'aammundi'

from rest_framework import serializers
from notifications.models import SyncNotification, BaseNotification
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


class AsyncNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncNotification
        fields = ('id', 'delivery_type', 'recipient', 'target', 'action_object', 'verb',
                  'start', 'end', 'notif_type', 'do_push')

    target = GenericSerializerField()
    action_object = GenericSerializerField(required=False)
    start = serializers.DateTimeField(required=False)
    end = serializers.DateTimeField(required=False)
    # AA Comments: notif_type needn't really be exposed in rest. Leaving it here for now.
    notif_type = serializers.IntegerField(required=False, default=verbs.WIZCARD_ENTITY_BROADCAST[0])
    do_push = serializers.BooleanField(required=False, default=True, write_only=True)

    def create(self, validated_data):
        delivery_mode = validated_data.pop('delivery_type', SyncNotification.EMAIL)
        start = validated_data.pop('start', timezone.now() + timedelta(minutes=1))
        end = validated_data.pop('end', timezone.now() + timedelta(minutes=1))

        # AA: Comments: this was broken
        push_notif = notify.send(
            self.context.get('user'),
            delivery_type=delivery_mode,
            start_date=start,
            end_date=end,
            **validated_data
        )

        return push_notif[0][1]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncNotification
        fields = ('id', 'recipient', 'target', 'action_object', 'verb', 'notif_type', 'delivery_mode',
                  'do_push', 'notification_text', 'start', 'end')

    target = GenericSerializerField()
    action_object = GenericSerializerField(required=False)
    do_push = serializers.BooleanField(required=False, default=False, write_only=True)
    start = serializers.DateTimeField(required=False, default=timezone.now(), write_only=True)
    end = serializers.DateTimeField(required=False, default=timezone.now(), write_only=True)
    notif_type = serializers.IntegerField(required=True)
    delivery_mode = serializers.ChoiceField(BaseNotification.DELIVERY_MODE, write_only=True)
    notification_text = serializers.CharField(required=False)

    def create(self, validated_data):
        start = validated_data.pop('start', timezone.now() + timedelta(minutes=1))
        end = validated_data.pop('end', timezone.now() + timedelta(minutes=1))
        notif_type = validated_data.pop('notif_type')

        push_notif = notify.send(
            self.context.get('user'),
            notif_type=notif_type,
            delivery_type=SyncNotification.DELIVERY_TYPE_ASYNC,
            start_date=start,
            end_date=end,
            **validated_data
        )

        return push_notif[0][1]



