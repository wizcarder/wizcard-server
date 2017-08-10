from media_components.models import MediaEntities
from media_components.serializers import  MediaEntitiesSerializer
from base_entity.views import BaseEntityComponentViewSet


class MediaEntitiesViewSet(BaseEntityComponentViewSet):
    queryset = MediaEntities.objects.all()
    serializer_class = MediaEntitiesSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = MediaEntities.objects.users_media(user)
        return queryset

    def get_serializer_context(self):
        return {'user': self.request.user}




