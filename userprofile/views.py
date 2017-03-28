# Create your views here.
from  userprofile.models import UserProfile
from rest_framework import viewsets, serializers
import django_filters

import pdb

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (['id', 'userid'])

class UserQueryFilter(django_filters.rest_framework.FilterSet):
    email = django_filters.CharFilter(name="user__email")
    username = django_filters.CharFilter(name="user__username")

    class Meta:
        model = UserProfile
        fields = ['email', 'username']


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer
    filter_class = UserQueryFilter




