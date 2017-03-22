# Create your views here.
from  userprofile.models import UserProfile
from rest_framework import viewsets, serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (['id', 'userid'])


class UserViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer
    filter_fields = ('user__email', 'user__username')


