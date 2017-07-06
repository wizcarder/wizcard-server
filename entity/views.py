from rest_framework import viewsets
from rest_framework.response import Response
from entity.models import BaseEntity, Event, Product, EventComponent, Business, VirtualTable, Speaker, Sponsor
from entity.serializers import EntitySerializerL2, EventSerializer, EventSerializerL2 ,ProductSerializer, \
    BusinessSerializer, TableSerializer, SpeakerSerializer, SponsorSerializer, EventComponentSerializer
from django.http import Http404
from django.contrib.auth.models import User
from rest_framework.decorators import detail_route
from email_and_push_infra.models import EmailEvent
from email_and_push_infra.signals import email_trigger
from rest_framework import status
import pdb


# Create your views here.

class BaseEntityViewSet(viewsets.ModelViewSet):
    queryset = BaseEntity.objects.all()
    serializer_class = EntitySerializerL2

    def get_queryset(self):
        #if isinstance(self, BaseEntityViewSet):
         #   queryset = BaseEntity.objects.all()
        user = self.request.user
        queryset = BaseEntity.objects.users_entities(user)
        return queryset

    def perform_create(self, serializer):
        instance = serializer.save(creator=self.request.user)
        instance.join(self.request.user)

    def get_serializer_context(self):
        return {'user': self.request.user}



class EventViewSet(BaseEntityViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_serializer_class(self):
        user = self.request.user
        if self.request.method == 'GET' and user is not None:
            return EventSerializerL2
        return EventSerializer


    def get_object_or_404(self, pk):
        try:
            return Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            raise Http404

    def get_queryset(self):
        user = self.request.user
        queryset = Event.objects.users_entities(user)
        return queryset
        #queryset = Event.objects.all()
        #return super(EventViewSet, self).get_queryset()



    def update(self, request, pk=None, partial=True):
        inst = self.get_object_or_404(pk)
        serializer = EventSerializer(inst, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
        else:
            raise Http404
        return Response(serializer.data)

    @detail_route(methods=['post'])
    def invite_exhibitors(self, request, pk=None):
        inst = self.get_object_or_404(pk)
        emails = request.data
        for recp in emails['email']:
            email_trigger.send(inst, source=inst, trigger=EmailEvent.INVITE_EXHIBITOR, to_email=recp)
        return Response("Exhibitors email added", status=status.HTTP_201_CREATED)


class ProductViewSet(BaseEntityViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Product.objects.users_entities(user)
        return queryset
        #queryset = Product.objects.all()
        #super(ProductViewSet, self).get_queryset()


class BusinessViewSet(BaseEntityViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Business.objects.users_entities(user)
        return queryset
        #queryset = Business.objects.all()
        #super(BusinessViewSet, self).get_queryset()


class TableViewSet(BaseEntityViewSet):
    queryset = VirtualTable.objects.all()
    serializer_class = TableSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = VirtualTable.objects.users_entities(user)
        return queryset
        #queryset = VirtualTable.objects.all()
        #super(TableViewSet, self).get_queryset()


class EventComponentViewSet(viewsets.ModelViewSet):
    queryset = EventComponent.objects.all()
    serializer_class = EventComponentSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = EventComponent.objects.users_components(user)
        return queryset


    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class SpeakerViewSet(EventComponentViewSet):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Speaker.objects.users_components(user)
        return queryset
        #queryset = Speaker.objects.all()
        #return super(SpeakerViewSet, self).get_queryset()
'''
    def get_serializer_context(self):
        user = 
        uid = self.request.query_params.get('user', None)
        if uid is not None:
            user = User.objects.get(id=uid)
            return {'user': user}
        else:
            return {}
'''


class SponsorViewSet(viewsets.ModelViewSet):
    queryset = Sponsor.objects.all()
    serializer_class = SponsorSerializer

    def get_queryset(self):
        queryset = Sponsor.objects.all()
        return super(SponsorViewSet, self).get_queryset()

'''
    def get_serializer_context(self):
        uid = self.request.query_params.get('user', None)
        if uid is not None:
            user = User.objects.get(id=uid)
            return {'user': user}
        else:
            return {}
'''


