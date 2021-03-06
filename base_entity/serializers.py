from rest_framework import serializers
from rest_framework.validators import ValidationError
from location_mgr.serializers import LocationSerializerField
from base_entity.models import BaseEntity, EntityEngagementStats, BaseEntityComponent, EntityUserStats
from entity.models import CoOwners
from media_components.serializers import MediaEntitiesSerializer
from wizserver import verbs
from django.contrib.contenttypes.models import ContentType

import pdb


class RelatedSerializerField(serializers.RelatedField):

    def get_queryset(self):
        pass

    def to_internal_value(self, data):

        ids = data.get('ids', None)
        etype = data.get('type', None)

        # Perform the data validation.
        if ids is None:
            raise ValidationError({
                'ids': 'This field is required.'
            })
        if not type:
            raise ValidationError({
                'type': 'This field is required.'
            })

        value_dict = {'ids': ids, 'type': etype}

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
    # we may not use this directly. Keeping it here for future
    join_fields = serializers.SerializerMethodField()

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

    def get_join_fields(self, obj):
        parent = self.context.get('parent', None)
        if not parent:
            return {}

        # AA: Yes it's tempting to check if there is indeed a join_table row
        # before accessing join_fields. However, if there isn't a join_table
        # row in this path, considering there is a valid 'parent' provided,
        # there is something else that's wrong. masking the access will simply
        # push the real issue under the rug

        join_table_row = parent.get_join_table_row(obj)
        # AA: Later Found a valid case to error check. If an exhibitor gets
        # linked and then unlinked...if those notifs are sent in the same
        # envelope to the app, then when building the response for the "C"
        # part, the join table won't be there.
        if join_table_row:
            return join_table_row.join_fields

        return {}

    def prepare(self, validated_data):
        self._owners = validated_data.pop('owners', None)
        self._sub_entities = validated_data.pop('related', None)
        self._location = validated_data.pop('location', None)
        self._users = validated_data.pop('users', None)
        self._tags = validated_data.pop('taganomy', None)

    def create(self, validated_data):
        cls = BaseEntityComponent.entity_cls_from_type(validated_data['entity_type'])

        obj = BaseEntityComponent.create(
            cls,
            owner=self.context.get('user'),
            is_creator=True,
            **validated_data
        )

        return obj

    def post_create_update(self, entity, update=False):
        # update arg is not really used. Leaving it here in case we need it down the line

        if hasattr(self, '_owners') and self._owners:
            BaseEntityComponent.add_owners(entity, self._owners)

        if hasattr(self, '_sub_entities') and self._sub_entities:
            for s in self._sub_entities:
                # looks like only media is the sub-entity here. The rest come via nested
                # this path will not result in notifs.
                entity.add_remove_sub_entities_of_type(s.get('ids'), s.get('type'))

        if hasattr(self, '_location') and self._location:
            entity.create_or_update_location(self._location['lat'], self._location['lng'])

        if hasattr(self, '_tags') and self._tags:
            taganomy = self._tags['taganomy']
            tags = self._tags['tags']

            taganomy.register_object(entity)

            taganomy.tags.add(*tags)
            entity.tags.set(*tags)

        notif_operation = verbs.NOTIF_OPERATION_UPDATE if update else verbs.NOTIF_OPERATION_CREATE
        BaseEntityComponent.objects.notify_via_entity_parent(
            entity,
            verbs.WIZCARD_ENTITY_UPDATE,
            notif_operation
        )

        return entity
