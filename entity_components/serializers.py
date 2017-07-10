__author__ = 'aammundi'

from rest_framework import serializers
from entity_components.models import Speaker, Sponsor
from media_mgr.models import MediaObjects

class SpeakerSerializer(serializers.ModelSerializer):
    media = serializers.PrimaryKeyRelatedField(many=True, required=False, queryset=MediaObjects.objects.all())
    ext_fields = serializers.DictField(required=False)

    class Meta:
        model = Speaker
        fields = ('id', 'website', 'description', 'ext_fields', 'company', 'title', 'vcard', 'media',)
        read_only_fields = ('vcard',)

    def create(self, validated_data):
        s = Speaker.objects.create(**validated_data)
        return s

    def update(self, instance, validated_data):
        instance.first_name = validated_data.pop("first_name", instance.first_name)
        instance.last_name = validated_data.pop("last_name", instance.last_name)
        instance.phone = validated_data.pop("phone", instance.phone)
        instance.email = validated_data.pop("email", instance.email)
        instance.company = validated_data.pop("org", instance.company)
        instance.title = validated_data.pop("title", instance.title)
        instance.ext_fields = validated_data.pop("ext_fields", instance.ext_fields)
        instance.description = validated_data.pop("description", instance.description)
        instance.save()

        instance = super(SpeakerSerializer, self).update(instance, validated_data)
        return instance

class SponsorSerializer(serializers.Serializer):
    class Meta:
        model = Sponsor
        fields = "__all__"

    media = serializers.PrimaryKeyRelatedField(many=True, required=False, queryset=MediaObjects.objects.all())

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

