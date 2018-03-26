from rest_framework.response import Response
from rest_framework import status
from base_entity.views import BaseEntityComponentViewSet
from polls.serializers import QuestionSerializer, QuestionChoicesSerializer
from entity.serializers import PollSerializer, PollResponseSerializer
from polls.models import Poll, Question, QuestionChoicesBase
from rest_framework.decorators import detail_route
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
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

    @detail_route(methods=['post'], url_path='activate')
    def publish_poll(self, request, pk=None):
        inst = get_object_or_404(Poll, pk=pk)
        inst.set_entity_state(BaseEntityComponent.ENTITY_STATE_PUBLISHED)

        return Response("poll id %s published" % pk, status=status.HTTP_200_OK)

    @detail_route(methods=['post'], url_path='link')
    def link_to_entity(self, request, pk):
        poll = get_object_or_404(Poll, pk=pk)
        entity_type = request.POST['entity_type']
        entity_id = request.POST['entity_id']

        # maybe we shouldn't attach a poll which is not activated ?
        if not poll.is_active():
            return Response("Please activate poll %s first. " % poll.description, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        c = BaseEntityComponent.entity_cls_from_type(entity_type)
        entity = get_object_or_404(c, pk=entity_id)

        entity.add_subentity_obj(poll, BaseEntityComponent.POLL)

        return Response("poll %s linked to entity" % poll.description, status=status.HTTP_200_OK)

    @detail_route(methods=['post'], url_path='unlink')
    def unlink_from_entity(self, request, pk):
        poll = get_object_or_404(Poll, pk=pk)
        entity_type = request.POST['entity_type']
        entity_id = request.POST['entity_id']

        c = BaseEntityComponent.entity_cls_from_type(entity_type)
        entity = get_object_or_404(c, entity_id)

        entity.remove_sub_entity_obj(poll, BaseEntityComponent.POLL)

        return Response("poll %s unlinked from entity" % poll.description, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        try:
            poll = Poll.objects.get(id=kwargs.get('pk'))
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PollSerializer(poll, request.data)
        if serializer.is_valid():
            inst = serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PollQuestionViewSet(BaseEntityComponentViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def list(self, request, **kwargs):
        poll = Poll.objects.get(id=kwargs.get('poll_pk'))
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

    def create(self, request, **kwargs):
        try:
            poll = Poll.objects.get(id=kwargs.get('poll_pk'))
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        request.data.update(poll=poll)

        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            inst = serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, poll_pk=None):
        try:
            poll = Poll.objects.get(id=poll_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not poll.questions.filter(id=pk).exists():
            return Response("question id %s not associated with Poll %s " % (pk, poll_pk),
                            status=status.HTTP_400_BAD_REQUEST)

        question = poll.questions.get(id=pk)
        request.data.update(poll=poll)

        serializer = QuestionSerializer(question, data=request.data)
        if serializer.is_valid():
            inst = serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    queryset = Poll.objects.all()
    serializer_class = PollResponseSerializer

    def list(self, request, **kwargs):
        poll = Poll.objects.get(id=kwargs.get('poll_pk'))
        return Response(PollResponseSerializer(poll).data)

