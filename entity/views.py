from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import generics
from entity.models import Event
from entity.serializers import EventSerializer
from rest_framework_extensions.mixins import NestedViewSetMixin
from media_mgr.serializers import MediaObjectsSerializer
from media_mgr.models import MediaObjects
from django.http import Http404
import pdb


# Create your views here.


class EventViewSet(viewsets.ModelViewSet):

    def get_object_or_404(self, pk):
        try:
            return Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            raise Http404

    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def retrieve(self, request, pk=None):
        queryset = Event.objects.get(id=pk)
        serializer = EventSerializer(queryset)
        return Response(serializer.data)

    def update(self, request, pk=None, partial=True):
        inst = self.get_object_or_404(pk)
        serializer = EventSerializer(inst, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

    def partial_update(self, request, pk=None):
        inst = self.get_object_or_404(pk)
        serializer = EventSerializer(inst, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)