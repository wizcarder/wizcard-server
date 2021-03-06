__author__ = 'aammundi'

from rest_framework import serializers
from notifications.models import AsyncNotification, SyncNotification, BaseNotification
from notifications.signals import notify
from rest_framework.validators import ValidationError
from django.contrib.contenttypes.models import ContentType
from wizserver import verbs
from django.utils import timezone
from datetime import timedelta
from userprofile.models import UserProfile


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
        model = AsyncNotification
        fields = ('id', 'target', 'action_object', 'notif_type', 'verb', 'notification_text',
                  'start', 'end',  'do_push')

    target = GenericSerializerField()
    action_object = GenericSerializerField(required=False)
    start = serializers.DateTimeField(required=False)
    end = serializers.DateTimeField(required=False)
    # AA Comments: notif_type needn't really be exposed in rest. Leaving it here for now.
    notif_type = serializers.IntegerField(
        required=False,
        default=verbs.get_notif_type(verbs.WIZCARD_ENTITY_BROADCAST)
    )
    verb = serializers.CharField(required=False)
    do_push = serializers.BooleanField(required=False, default=True, write_only=True)

    def create(self, validated_data):
        start = validated_data.pop('start', timezone.now() + timedelta(minutes=1))
        end = validated_data.pop('end', timezone.now() + timedelta(minutes=1))
        notif_type = validated_data.pop('notif_type')

        push_notif = notify.send(
            self.context.get('user'),
            # recipient is dummy
            recipient=UserProfile.objects.get_admin_user(),
            start_date=start,
            end_date=end,
            notif_tuple=verbs.notif_type_tuple_dict[notif_type],
            **validated_data
        )

        obj = push_notif[0][1]
        if not obj:
            raise serializers.ValidationError("No subscribers to notify")

        return obj


class SyncNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncNotification
        fields = ('id', 'target', 'action_object', 'notif_type', 'verb', 'notification_text')

    target = GenericSerializerField()
    action_object = GenericSerializerField(required=False)
    notif_type = serializers.IntegerField(required=True)
    notification_text = serializers.SerializerMethodField()
    verb = serializers.SerializerMethodField()

    def create(self, validated_data):
        start = validated_data.pop('start', timezone.now() + timedelta(minutes=1))
        end = validated_data.pop('end', timezone.now() + timedelta(minutes=1))
        notif_type = validated_data.pop('notif_type')

        push_notif = notify.send(
            self.context.get('user'),
            notif_type=notif_type,
            start_date=start,
            end_date=end,
            notif_tuple=verbs.notif_type_tuple_dict[notif_type],
            **validated_data
        )

        return push_notif[0][1]

    def get_notification_text(self, obj):
        return obj.notification_text.format(
            obj.target,
            obj.action_object
        )

    def get_verb(self, obj):
        return obj.verb.format(
            obj.target,
            obj.action_object
        )


