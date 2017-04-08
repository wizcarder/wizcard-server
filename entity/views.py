from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import generics
from entity.models import BaseEntity, Event, Product, Business
from entity.serializers import EntitySerializer, EventSerializer, ProductSerializer, BusinessSerializer
from rest_framework_extensions.mixins import NestedViewSetMixin
from media_mgr.serializers import MediaObjectsSerializer
from media_mgr.models import MediaObjects
from django.http import Http404
import pdb


# Create your views here.


class BaseEntityViewSet(viewsets.ModelViewSet):

    queryset = BaseEntity.objects.all()
    serializer_class = EntitySerializer

class EventViewSet(BaseEntityViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_object_or_404(self, pk):
        try:
            return Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            raise Http404

    def update(self, request, pk=None, partial=True):
        inst = self.get_object_or_404(pk)
        serializer = EventSerializer(inst, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)

   



class ProductViewSet(BaseEntityViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class BusinessViewSet(BaseEntityViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
