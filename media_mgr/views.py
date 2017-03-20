from rest_framework.response import Response
from rest_framework import viewsets
from media_mgr.models import MediaObjects
from media_mgr.serializers import MediaObjectsSerializer
from django.contrib.contenttypes.models import ContentType
import pdb

# Create your views here.

class MediaObjectsViewSet(viewsets.ModelViewSet):

    queryset = MediaObjects.objects.all()
    serializer_class = MediaObjectsSerializer

    def list(self, request, event_pk=None):
        queryset = self.queryset.filter(object_id=event_pk)
        serializer = MediaObjectsSerializer(queryset, many=True, data=request.data)
        return Response(serializer.data)

    def retrieve(self, request, event_pk=None, pk=None, **kwargs):
        queryset = MediaObjects.objects.filter(pk=pk, object_id=event_pk)
        serializer = MediaObjectsSerializer(queryset, many=True, data=request.data)
        return Response(serializer.data)

    # def get_queryset(self):
    #     pdb.set_trace()
    #     return super(MediaObjectsViewSet, self).get_queryset().filter(
    #         content_type=ContentType.objects.get_for_model(MediaObjects)
    #     )
