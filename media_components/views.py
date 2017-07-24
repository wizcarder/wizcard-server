from rest_framework import viewsets
from media_components.models import MediaEntities
from media_components.serializers import  MediaEntitiesSerializer
import pdb

# Create your views here.

class MediaEntitiesViewSet(viewsets.ModelViewSet):
    queryset = MediaEntities.objects.all()
    serializer_class = MediaEntitiesSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = MediaEntities.objects.users_media(user)
        return queryset

    def get_serializer_context(self):
        return {'user': self.request.user}




