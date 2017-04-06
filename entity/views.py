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

class ProductViewSet(BaseEntityViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class BusinessViewSet(BaseEntityViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
