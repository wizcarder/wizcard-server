from rest_framework.response import Response
from base_entity.models import BaseEntityComponent
from entity.models import Event, Campaign, VirtualTable,\
    Speaker, Sponsor, ExhibitorInvitee, AttendeeInvitee, Agenda, CoOwners
from entity.serializers import EventSerializer, EventSerializerL0, CampaignSerializer, \
    TableSerializer, AttendeeInviteeSerializer, ExhibitorInviteeSerializer, SponsorSerializer, \
    SpeakerSerializer, AgendaSerializer, CoOwnersSerializer
from media_components.serializers import MediaEntitiesSerializer
from media_components.models import MediaEntities
from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from taganomy.models import Taganomy
from taganomy.serializers import TaganomySerializer
from rest_framework.decorators import detail_route
from rest_framework import viewsets, status, mixins
from base_entity.views import BaseEntityViewSet, BaseEntityComponentViewSet
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from itertools import chain


import pdb


# Create your views here.

class ExhibitorEventViewSet(BaseEntityViewSet):
    serializer_class = EventSerializerL0

    def get_serializer_class(self):
        return EventSerializerL0

    def get_queryset(self):
        user = self.request.user
        queryset = Event.objects.users_entities(user)
        return queryset


class EventViewSet(BaseEntityViewSet):
    serializer_class = EventSerializer

    def get_serializer_class(self):
        return EventSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Event.objects.owners_entities(user)
        return queryset

    @detail_route(methods=['post'])
    def invite_exhibitors(self, request, pk=None):
        inst = get_object_or_404(Event, pk=pk)
        exhibitor_invitees = request.data['ids']

        # set related for these exhibitors. We will relate the entity to the ExhibitorInvitee model
        # and check for those events when the exhibitor comes in, treating the exhibitor email as the
        # handle within ExhibitorInvitee. Essentially, Exhibitor/AttendeeInvitee becomes the future user construct

        # exhibitor may already have an account. if so, join them to event
        existing_users, existing_exhibitors = ExhibitorInvitee.objects.check_existing_users_exhibitors(
            exhibitor_invitees
        )
        [inst.join(u, notify=False) for u in existing_users]

        for e in existing_exhibitors:
            e.state = ExhibitorInvitee.ACCEPTED
            e.save()

        new_exhibitors = [x for x in exhibitor_invitees if x not in existing_exhibitors.values_list('id', flat=True)]

        # relate these with Event
        invited_exhibitors = inst.add_subentities(new_exhibitors, BaseEntityComponent.SUB_ENTITY_EXHIBITOR_INVITEE)
        for i in invited_exhibitors:
            i.state = ExhibitorInvitee.INVITED
            i.save()

        result_list = list(chain(existing_exhibitors, invited_exhibitors))
        return Response(ExhibitorInviteeSerializer(result_list, many=True).data)

    @detail_route(methods=['post'])
    def invite_attendees(self, request, pk=None):
        inst = get_object_or_404(Event, pk=pk)

        attendees = request.data

        valid_candidates = inst.add_subentities(attendees, BaseEntityComponent.SUB_ENTITY_ATTENDEE_INVITEE)

        return Response(AttendeeInviteeSerializer(valid_candidates, many=True)).data

    @detail_route(methods=['get'])
    def publish_event(self, request, pk=None):
        inst = get_object_or_404(Event, pk=pk)
        inst.make_live()
        return Response("event id %s activated" % pk, status=status.HTTP_200_OK)


class CampaignViewSet(BaseEntityViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Campaign.objects.owners_entities(user)
        return queryset


class TableViewSet(BaseEntityViewSet):
    queryset = VirtualTable.objects.all()
    serializer_class = TableSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = VirtualTable.objects.owners_entities(user)
        return queryset


class SpeakerViewSet(BaseEntityComponentViewSet):
    queryset = Speaker.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = Speaker.objects.owners_entities(user)
        return queryset

    def get_serializer_class(self):
        return SpeakerSerializer


class SponsorViewSet(BaseEntityComponentViewSet):
    queryset = Sponsor.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = Sponsor.objects.owners_entities(user)
        return queryset

    def get_serializer_class(self):
        return SponsorSerializer


class ExhibitorViewSet(BaseEntityComponentViewSet):
    queryset = ExhibitorInvitee.objects.all()
    serializer_class = ExhibitorInviteeSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = ExhibitorInvitee.objects.owners_entities(user)
        return queryset


class AgendaViewSet(BaseEntityComponentViewSet):
    queryset = Agenda.objects.all()
    serializer_class = AgendaSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Agenda.objects.owners_entities(user)
        return queryset

    def get_serializer_class(self):
        return AgendaSerializer


class AttendeeViewSet(BaseEntityComponentViewSet):
    queryset = AttendeeInvitee.objects.all()
    serializer_class = AttendeeInviteeSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = AttendeeInvitee.objects.owners_entities(user)
        return queryset


class CoOwnerViewSet(BaseEntityComponentViewSet):
    queryset = CoOwners.objects.all()
    serializer_class = CoOwnersSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = CoOwners.objects.owners_entities(user)
        return queryset


"""
All the nested end-points for linking entity to sub-entity
"""


class EventCampaignViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer

    def list(self, request, event_pk=None):
        event = Event.objects.get(id=event_pk)
        cpg = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_CAMPAIGN)
        return Response(CampaignSerializer(cpg, many=True).data)

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            cpg = Campaign.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if cpg not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_CAMPAIGN):
            return Response("event id %s not associated with Agenda %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(CampaignSerializer(cpg).data)

    def create(self, request, event_pk=None):
        try:
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CampaignSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_CAMPAIGN)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventSpeakerViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer

    def list(self, request, event_pk=None):
        event = Event.objects.get(id=event_pk)
        spk = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_SPEAKER)
        return Response(SpeakerSerializer(spk, many=True).data)

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            spk = Speaker.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if spk not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_SPEAKER):
            return Response("event id %s not associated with Speaker %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(SpeakerSerializer(spk).data)

    def create(self, request, event_pk=None):
        try:
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = SpeakerSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_SPEAKER)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventSponsorViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = Sponsor.objects.all()
    serializer_class = SpeakerSerializer

    def list(self, request, event_pk=None):
        event = Event.objects.get(id=event_pk)
        spn = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_SPONSOR)
        return Response(SpeakerSerializer(spn, many=True).data)

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            spn = Sponsor.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if spn not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_SPONSOR):
            return Response("event id %s not associated with Sponsor %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(SponsorSerializer(spn).data)

    def create(self, request, event_pk=None):
        try:
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = SponsorSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_SPONSOR)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventMediaViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = MediaEntities.objects.all()
    serializer_class = MediaEntitiesSerializer

    def list(self, request, event_pk=None):
        event = Event.objects.get(id=event_pk)
        med = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_MEDIA)
        return Response(MediaEntitiesSerializer(med, many=True).data)

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            med = MediaEntities.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if med not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_MEDIA):
            return Response("event id %s not associated with Media %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(SponsorSerializer(med).data)

    def create(self, request, event_pk=None):
        try:
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = MediaEntitiesSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_MEDIA)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventAttendeeViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = AttendeeInvitee.objects.all()
    serializer_class = AttendeeInviteeSerializer

    def list(self, request, event_pk=None):
        event = Event.objects.get(id=event_pk)
        ati = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_ATTENDEE_INVITEE)
        return Response(AttendeeInviteeSerializer(ati, many=True).data)

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            ati = AttendeeInvitee.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if ati not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_ATTENDEE_INVITEE):
            return Response("event id %s not associated with invitee %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(AttendeeInviteeSerializer(ati).data)

    def create(self, request, event_pk=None):
        try:
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = AttendeeInviteeSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_ATTENDEE_INVITEE)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventCoOwnerViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = CoOwners.objects.all()
    serializer_class = CoOwnersSerializer

    def list(self, request, event_pk=None):
        event = Event.objects.get(id=event_pk)
        ati = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_COOWNER)
        return Response(CoOwnersSerializer(ati, many=True).data)

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            coo = CoOwners.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if coo not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_COOWNER):
            return Response("event id %s not associated with co-owner %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(CoOwnersSerializer(coo).data)

    def create(self, request, event_pk=None):
        try:
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CoOwnersSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_COOWNER)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventAgendaViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = Agenda.objects.all()
    serializer_class = AgendaSerializer

    def list(self, request, event_pk=None):
        event = Event.objects.get(id=event_pk)
        agn = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_AGENDA)
        return Response(AgendaSerializer(agn, many=True).data)

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            agn = Agenda.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if agn not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_AGENDA):
            return Response("event id %s not associated with Agenda %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(AgendaSerializer(agn).data)

    def create(self, request, event_pk=None):
        try:
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = AgendaSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_AGENDA)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventNotificationViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin,
                               mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = Notification.objects.all()
    serializer_class = TaganomySerializer

    def list(self, request, event_pk=None):
        event = Event.objects.get(id=event_pk)
        ntf = Notification.objects.event_notifications(event)

        return Response(NotificationSerializer(ntf, many=True).data)

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            ntf = Notification.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(NotificationSerializer(ntf).data)

    def create(self, request, event_pk=None):
        try:
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = NotificationSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventTagonomyViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = Taganomy.objects.all()
    serializer_class = TaganomySerializer

    def list(self, request, event_pk=None):
        event = Event.objects.get(id=event_pk)
        cat = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_CATEGORY)
        return Response(TaganomySerializer(cat, many=True).data)

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            cat = Taganomy.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if cat not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_CATEGORY):
            return Response("event id %s not associated with category %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(TaganomySerializer(cat).data)

    def create(self, request, event_pk=None):
        try:
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = TaganomySerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_CATEGORY)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

