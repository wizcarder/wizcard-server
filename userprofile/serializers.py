from rest_framework import serializers
from django.contrib.auth.models import User
from userprofile.models import UserProfile
from rest_framework.validators import ValidationError
import hashlib
import pdb


class UserSerializerL0(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('user_id', 'username', 'email', 'first_name', 'last_name', 'user_type',)

    user_id = serializers.PrimaryKeyRelatedField(source='id', read_only=True)
    email = serializers.EmailField()
    user_type = serializers.IntegerField(source='profile.user_type')

    def create(self, validated_data):
        user_type = validated_data.pop('profile')['user_type']
        if user_type not in [
            UserProfile.APP_USER,
            UserProfile.WEB_ORGANIZER_USER,
            UserProfile.WEB_EXHIBITOR_USER,
            UserProfile.PORTAL_USER_INTERNAL
        ]:
            raise ValidationError({
                'user_type': 'invalid field value'
            })

        # need to fix this.
        password = validated_data.get('email')
        username = validated_data.get('username')
        user, created = User.objects.get_or_create(username=username, defaults=validated_data)

        if created:
            user.set_password(hashlib.sha1(password).hexdigest())
        user.save()

        profile = user.profile
        profile.create_user_type(user_type)

        return user

    def update(self, instance, validated_data):
        user_type = validated_data.pop('profile')['user_type']
        if user_type not in [
            UserProfile.APP_USER,
            UserProfile.WEB_ORGANIZER_USER,
            UserProfile.WEB_EXHIBITOR_USER,
            UserProfile.PORTAL_USER_INTERNAL
        ]:
            raise ValidationError({
                'user_type': 'invalid field value'
            })

        instance = super(UserSerializerL0, self).update(instance, validated_data)

        instance.profile.add_user_type(user_type)

        return instance


# used by portal
class UserSerializer(UserSerializerL0):
    class Meta(UserSerializerL0.Meta):
        model = User
        fields = UserSerializerL0.Meta.fields

