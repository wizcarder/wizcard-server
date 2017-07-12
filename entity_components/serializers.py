__author__ = 'aammundi'

from rest_framework import serializers
from entity_components.models import Speaker, Sponsor, MediaEntities
from media_mgr.serializers import MediaObjectsSerializer
from media_mgr.models import MediaObjects
from entity.models import BaseEntityComponent


class BaseEntityComponentSerializer(serializers.ModelSerializer):
    related_entities = serializers.PrimaryKeyRelatedField(many=True,
                                                          required=False,
                                                          queryset=BaseEntityComponent.objects.all())
    ext_fields = serializers.DictField(required=False)

    class Meta:
        model = BaseEntityComponent
        fields = '__all__'

    def prepare(self, validated_data):
        self.related_entities = validated_data.pop('related_entities')

    def post_create(self, obj):
        obj.add_related(self.related_entities)
        return obj



class SpeakerSerializerL1(BaseEntityComponentSerializer):
    # def __init__(self, *args, **kwargs):
    #     many = kwargs.pop('many', True)
    #     super(SpeakerSerializer, self).__init__(many=many, *args, **kwargs)

    class Meta:
        model = Speaker
        fields = '__all__'
        read_only_fields = ('vcard',)



    def create(self, validated_data, **kwargs):
        self.prepare(validated_data)
        spkr = BaseEntityComponent.create(Speaker, owner=self.context.get('user'), is_creator=True, **validated_data)
        self.post_create(spkr)
        return spkr



class SpeakerSerializerL2(SpeakerSerializerL1):
   # related_entities = RelatedEntitiesField()

    class Meta:
        model = Speaker
        fields = '__all__'


class SponsorSerializerL1(BaseEntityComponentSerializer):
    class Meta:
        model = Sponsor
        fields = "__all__"
        read_only_fields = ('vcard',)

    def create(self, validated_data):
        self.prepare(validated_data)
        spn = BaseEntityComponent.create(Sponsor, owner=self.context.get('user'), is_creator=True, **validated_data)
        self.post_create(spn)
        return spn


class SponsorSerializerL2(SponsorSerializerL1):
    #media = MediaObjectsSerializer(many=True)

    class Meta:
        model = Sponsor
        fields = '__all__'


class MediaEntitiesSerializer(BaseEntityComponentSerializer):
    class Meta:
        model = MediaEntities
        fields = '__all__'


    def create(self, validated_data):
        user = self.context.get('user')
        mobj = BaseEntityComponent.create(MediaEntities, owner=user, is_creator=True, **validated_data)
        return mobj



