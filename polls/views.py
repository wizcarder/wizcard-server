from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets, status
from base_entity.views import BaseEntityComponentViewSet
from polls.serializers import PollSerializer, QuestionSerializer, QuestionChoicesSerializer
from polls.models import Poll, Question, QuestionChoicesBase

import pdb
# Create your views here.

class PollViewSet(BaseEntityComponentViewSet):

    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Poll.objects.owners_entities(user)
        return queryset


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
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not poll.questions.filter(id=pk).exists():
            return Response("question id %s not associated with Poll %s " % (pk, poll_pk),
                            status=status.HTTP_400_BAD_REQUEST)

        question = poll.questions.get(id=pk)

        return Response(QuestionSerializer(question).data)

    def update(self, request, pk=None, poll_pk=None):
        try:
            poll = Poll.objects.get(id=poll_pk)
        except:
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
        except:
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
        except:
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