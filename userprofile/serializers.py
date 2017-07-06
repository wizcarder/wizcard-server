from rest_framework import serializers
from django.contrib.auth.models import User
from userprofile.models import UserProfile
from rest_framework.validators import ValidationError
import hashlib

from allauth.account import app_settings as allauth_settings
from allauth.utils import email_address_exists
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from rest_auth.registration.serializers import RegisterSerializer
import pdb

class UserRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=False, write_only=True)
    last_name = serializers.CharField(required=False, write_only=True)
    user_type = serializers.IntegerField(source='profile.user_type')

    def get_cleaned_data(self):
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'password1': self.validated_data.get('password1', ''),
            'username': self.validated_data.get('username', ''),
            'email': self.validated_data.get('email', ''),
            'user_type': self.validated_data.get('profile')['user_type']
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user_type = self.cleaned_data.pop('user_type')
        if user_type not in [
            UserProfile.APP_USER,
            UserProfile.WEB_ORGANIZER_USER,
            UserProfile.WEB_EXHIBITOR_USER,
            UserProfile.PORTAL_USER_INTERNAL
        ]:
            raise ValidationError({
                'user_type': 'invalid field value'
            })
        adapter.save_user(request, user, self)
        setup_user_email(request, user, [])
        user.save()
        profile = user.profile.create_user_type(int(user_type))
        return user



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

