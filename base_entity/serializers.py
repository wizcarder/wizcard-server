from rest_framework import serializers
from rest_framework.validators import ValidationError
from location_mgr.serializers import LocationSerializerField
from base_entity.models import BaseEntity, EntityEngagementStats, BaseEntityComponent, EntityUserStats
from entity.models import CoOwners
from media_components.serializers import MediaEntitiesSerializer
from wizserver import verbs
import pdb


class RelatedSerializerField(serializers.RelatedField):

    def get_queryset(self):
        pass

    def to_internal_value(self, data):

        ids = data.get('ids', None)
        etype = data.get('type', None)
        overwrite = data.get('overwrite', False)

        # Perform the data validation.
        if ids is None:
            raise ValidationError({
                'ids': 'This field is required.'
            })
        if not type:
            raise ValidationError({
                'type': 'This field is required.'
            })

        value_dict = {'ids': ids, 'type': etype, 'overwrite': overwrite}

        return value_dict

    def to_representation(self, value):
        pass


class EntityEngagementSerializer(serializers.Serializer):
    class Meta:
        model = EntityEngagementStats
        fields = ('like_count', 'agg_like_level', 'views', 'follows', 'unfollows')

    like_level = serializers.SerializerMethodField(read_only=True)

    def get_like_level(self, obj):
        user = self.context.get('user')
        if EntityUserStats.objects.filter(user=user, stats=obj).exists():
            user_stat = EntityUserStats.objects.get(user=user, stats=obj)
            return user_stat.like_level

        return EntityUserStats.MIN_ENGAGEMENT_LEVEL


class EntitySerializerL0(serializers.ModelSerializer):
    class Meta:
        model = BaseEntity
        fields = ('id', 'entity_type', 'num_users')


class EntityEngagementSerializerL1(EntityEngagementSerializer):
    class Meta:
        model = EntityEngagementStats
        my_fields = ('entity',)
        fields = EntityEngagementSerializer.Meta.fields + my_fields

    entity = EntitySerializerL0(read_only=True, source='engagements_baseentity_related')


"""
One Serializer with everything in it. This can be subclassed and individual fields
can be defined as needed and methods overridden.
This serializer should not be directly used
"""


class EntitySerializer(EntitySerializerL0):
    media = serializers.SerializerMethodField()
    location = LocationSerializerField(required=False)
    users = serializers.SerializerMethodField()
    friends = serializers.SerializerMethodField()
    like = serializers.SerializerMethodField()
    engagements = EntityEngagementSerializer(read_only=True)
    owners = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CoOwners.objects.all(),
        required=False,
        write_only=True
    )
    related = RelatedSerializerField(write_only=True, required=False, many=True)
    ext_fields = serializers.DictField(required=False)
    user_state = serializers.SerializerMethodField()

    MAX_THUMBNAIL_UI_LIMIT = 4

    class Meta(EntitySerializerL0.Meta):
        model = BaseEntity
        my_fields = ('name', 'address', 'venue',  'secure', 'description', 'email', 'website', 'phone',
                     'media', 'location', 'users', 'friends', 'like', 'user_state', 'entity_state',
                     'engagements', 'owners', 'related', 'ext_fields',)

        fields = EntitySerializerL0.Meta.fields + my_fields

    def get_media(self, obj):
        return MediaEntitiesSerializer(
            obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_MEDIA),
            many=True,
            context=self.context
        ).data

    def get_users(self, obj):
        return ""

    def get_creator(self, obj):
        return ""

    def get_friends(self, obj):
        return ""

    def get_user_state(self, obj):
        return obj.user_state(self.context.get('user'))

    def get_like(self, obj):
        liked, level = obj.engagements.user_liked(self.context.get('user'))
        return dict(liked=liked, like_level=level)

    def prepare(self, validated_data):
        self.owners = validated_data.pop('owners', None)
        self.sub_entities = validated_data.pop('related', None)
        self.location = validated_data.pop('location', None)
        self.users = validated_data.pop('users', None)
        self.tags = validated_data.pop('tags', None)

    def create(self, validated_data):
        cls, ser = BaseEntityComponent.entity_cls_ser_from_type(validated_data['entity_type'])

        obj = BaseEntityComponent.create(
            cls,
            owner=self.context.get('user'),
            is_creator=True,
            **validated_data
        )

        return obj

    def post_create_update(self, entity, update=False):
        if self.owners:
            BaseEntityComponent.add_owners(entity, self.owners)

        if self.sub_entities:
            for s in self.sub_entities:
                overwrite = s.pop('overwrite')
                if overwrite:
                    entity.remove_sub_entities_of_type(s['type'])
   
                entity.add_subentities(**s)

        if self.location:
            entity.create_or_update_location(self.location['lat'], self.location['lng'])

        if hasattr(self, 'tags'):
            taganomy = self.tags['taganomy']
            tags = self.tags['tags']
            taganomy.register_object(entity)
            entity.tags.set(*tags)

        # send entity_update (with sub_entity granularity)
        BaseEntityComponent.objects.notify_via_entity_parent(entity, verbs.WIZCARD_ENTITY_UPDATE)

        return entity
