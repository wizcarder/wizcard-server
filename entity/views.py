from rest_framework import viewsets
from rest_framework.response import Response
from entity.models import BaseEntity, Event, Product, Business, VirtualTable, Speaker
from entity.serializers import EntitySerializer, EventSerializer, ProductSerializer, \
    BusinessSerializer, TableSerializer, SpeakerSerializer, EventSerializerExpanded
from django.http import Http404
from rest_framework.decorators import detail_route
from email_and_push_infra.models import EmailEvent
from email_and_push_infra.signals import email_trigger
from rest_framework import status
import pdb


# Create your views here.

class BaseEntityViewSet(viewsets.ModelViewSet):
    queryset = BaseEntity.objects.all()
    serializer_class = EntitySerializer

class EventViewSet(BaseEntityViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EventSerializerExpanded
        return EventSerializer

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

    @detail_route(methods=['post'])
    def invite_exhibitors(self, request, pk=None):
        inst = self.get_object_or_404(pk)
        emails = request.data
        for email in emails:
            email_trigger.send(inst, source=inst, trigger=EmailEvent.INVITE_EXHIBITOR, to_email=email)
        return Response("Exhibitors email added", status=status.HTTP_201_CREATED)


class ProductViewSet(BaseEntityViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class BusinessViewSet(BaseEntityViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer


class TableViewSet(viewsets.ModelViewSet):
    queryset = VirtualTable.objects.all()
    serializer_class = TableSerializer


class SpeakerViewSet(viewsets.ModelViewSet):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer

