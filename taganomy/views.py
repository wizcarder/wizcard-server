
from taganomy.models import Taganomy
from taganomy.serializers import TaganomySerializer
from base_entity.views import BaseEntityComponentViewSet


# Create your views here.
class TaganomyViewSet(BaseEntityComponentViewSet):
    queryset = Taganomy.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = Taganomy.objects.owners_entities(user)
        return queryset

    def get_serializer_class(self):
        return TaganomySerializer
