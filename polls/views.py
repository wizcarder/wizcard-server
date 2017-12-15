from rest_framework.response import Response
from rest_framework import status
from base_entity.views import BaseEntityComponentViewSet
from polls.serializers import QuestionSerializer, QuestionChoicesSerializer
from entity.serializers import PollSerializer, PollResponseSerializer
from polls.models import Poll, Question, QuestionChoicesBase, UserResponse
from rest_framework.decorators import detail_route
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from entity.models import Event
from base_entity.models import BaseEntityComponent

import pdb
# Create your views here.


class PollViewSet(BaseEntityComponentViewSet):

    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Poll.objects.owners_entities(user)
        return queryset

    @detail_route(methods=['get'], url_path='activate')
    def publish_poll(self, request, pk=None):
        inst = get_object_or_404(Poll, pk=pk)
        inst.set_state(Poll.POLL_STATE_ACTIVE)

        return Response("poll id %s activated" % pk, status=status.HTTP_200_OK)

    @detail_route(methods=['post'], url_path='attach')
    def attach_event(self, request, pk=None):
        event = get_object_or_404(Event, pk=request.POST['event_id'])
        poll = get_object_or_404(Poll, pk=pk)
        event.add_subentity_obj(poll, BaseEntityComponent.SUB_ENTITY_POLL)

        return Response("poll  %s attached to event" % poll.description, status=status.HTTP_200_OK)


class PollQuestionViewSet(BaseEntityComponentViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def list(self, request, poll_pk=None):
        poll = Poll.objects.get(id=poll_pk)
        questions = poll.questions.all()
        return Response(QuestionSerializer(questions, many=True).data)

    def retrieve(self, request, pk=None, poll_pk=None):
        try:
            poll = Poll.objects.get(id=poll_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not poll.questions.filter(id=pk).exists():
            return Response("question id %s not associated with Poll %s " % (pk, poll_pk),
                            status=status.HTTP_400_BAD_REQUEST)

        question = poll.questions.get(id=pk)

        return Response(QuestionSerializer(question).data)

    def update(self, request, pk=None, poll_pk=None):
        try:
            poll = Poll.objects.get(id=poll_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not poll.questions.filter(id=pk).exists():
            return Response("question id %s not associated with Poll %s " % (pk, poll_pk),
                            status=status.HTTP_400_BAD_REQUEST)

        question = poll.questions.get(id=pk)

        serializer = QuestionSerializer(question, data=request.data)
        if serializer.is_valid():
            inst = serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, pk=None, poll_pk=None):
        try:
            poll = Poll.objects.get(id=poll_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not poll.questions.filter(id=pk).exists():
            return Response("question id %s not associated with Poll %s " % (pk, poll_pk),
                            status=status.HTTP_400_BAD_REQUEST)

        question = poll.questions.get(id=pk)

        serializer = PollSerializer(question, data=request.data)
        if serializer.is_valid():
            inst = serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None, poll_pk=None):
        try:
            poll = Poll.objects.get(id=poll_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not poll.questions.filter(id=pk).exists():
            return Response("question id %s not associated with Poll %s " % (pk, poll_pk),
                            status=status.HTTP_400_BAD_REQUEST)

        question = poll.questions.get(id=pk)

        question.delete()

        return Response(status=status.HTTP_200_OK)


class PollQuestionChoicesViewSet(BaseEntityComponentViewSet):
    queryset = QuestionChoicesBase.objects.all()
    serializer_class = QuestionChoicesSerializer


class PollAnswersViewSet(BaseEntityComponentViewSet):
    queryset = UserResponse.objects.all()
    serializer_class = PollResponseSerializer

    def get_queryset(self):
        user = self.request.user

        # the answers this user is allowed to access are those associated
        # with the polls this guy owns
        poll_ids = Poll.objects.owners_entities(user).values_list('id', flat=True)
        queryset = UserResponse.objects.filter(poll_id__in=poll_ids)
        return queryset
