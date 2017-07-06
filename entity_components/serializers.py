__author__ = 'aammundi'

from rest_framework import serializers
from entity_components.models import  Speaker, EventComponentMixin, Sponsor
from media_mgr.serializers import MediaObjectsSerializer
from media_mgr.signals import media_create

class EventComponentSerializer(serializers.ModelSerializer):
    media = MediaObjectsSerializer(many=True, required=False)
    caption = serializers.CharField(required=False)

    class Meta:
        model = EventComponentMixin
        fields = "__all__"

    def prepare(self, validated_data):
        self.media = validated_data.pop('media', None)

    def post_create(self, component):
        if self.media:
            media_create.send(sender=component, objs=self.media)

        return component

    def update(self, instance, validated_data):
        instance.caption = validated_data.pop('caption', instance.caption)

        # handle related objects. It's a replace
        media = validated_data.pop('media', None)
        if media:
            instance.media.all().delete()
            media_create.send(sender=instance, objs=media)
        instance.save()
        return instance


class SpeakerSerializer(EventComponentSerializer):
    # def __init__(self, *args, **kwargs):
    #     many = kwargs.pop('many', True)
    #     super(SpeakerSerializer, self).__init__(many=many, *args, **kwargs)
    ext_fields = serializers.DictField(required=False)

    class Meta:
        model = Speaker
        fields = "__all__"
        read_only_fields = ('vcard',)

    def create(self, validated_data):
        self.prepare(validated_data)

        s = Speaker.objects.create(**validated_data)
        self.post_create(s)

        return s

    def update(self, instance, validated_data):
        instance.first_name = validated_data.pop("first_name", instance.first_name)
        instance.last_name = validated_data.pop("last_name", instance.last_name)
        instance.phone = validated_data.pop("phone", instance.phone)
        instance.email = validated_data.pop("email", instance.email)
        instance.org = validated_data.pop("org", instance.org)
        instance.designation = validated_data.pop("designation", instance.designation)
        instance.ext_fields = validated_data.pop("ext_fields", instance.ext_fields)
        instance.description = validated_data.pop("description", instance.description)
        instance.save()

        instance = super(SpeakerSerializer, self).update(instance, validated_data)
        return instance

class SponsorSerializer(EventComponentSerializer):
    class Meta:
        model = Sponsor
        fields = "__all__"

    def create(self, validated_data):
        self.prepare(validated_data)
        s = Sponsor.objects.create(**validated_data)
        self.post_create(s)
        return s

    def update(self, instance, validated_data):
        instance.name = validated_data.pop("name", instance.name)
        instance.save()
        instance = super(SponsorSerializer, self).update(instance, validated_data)
        return instance

