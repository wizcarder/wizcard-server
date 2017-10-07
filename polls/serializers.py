__author__ = 'aammundi'

from rest_framework import serializers
from polls.models import Poll, Question, QuestionChoicesBase
from base_entity.models import BaseEntityComponent
from entity.serializers import EntitySerializer

import pdb

class QuestionChoicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionChoicesBase
        fields = ('id', 'extra_text', 'question_key', 'question_value', 'low', 'high')

    question_key = serializers.CharField(required=False)
    question_value = serializers.CharField(required=False)
    low = serializers.CharField(required=False)
    high = serializers.CharField(required=False)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'question_type', 'ui_type', 'single_answer', 'question', 'poll', 'choices')

    choices = QuestionChoicesSerializer(many=True)
    poll = serializers.PrimaryKeyRelatedField(read_only=True)

    def update(self, instance, validated_data):
        choices = validated_data.pop('choices', [])

        # clear all choices
        instance.choices.all().delete()

        for c in choices:
            cls = Question.get_choice_cls_from_type(validated_data['question_type'])
            for c in choices:
                cls.objects.create(question=instance, **c)

        obj = super(QuestionSerializer, self).update(instance, validated_data)

        return obj


class PollSerializer(EntitySerializer):
    class Meta:
        model = Poll
        fields = ('id', 'description', 'questions')

    questions = QuestionSerializer(many=True)

    def prepare(self, validated_data):
        self.questions = validated_data.pop('questions', None)
        super(PollSerializer, self).prepare(validated_data)

    def post_create(self, obj):
        for q in self.questions:
            choices = q.pop('choices', [])
            q_inst = Question.objects.create(poll=obj, **q)

            cls = Question.get_choice_cls_from_type(q['question_type'])
            for c in choices:
                cls.objects.create(question=q_inst, **c)

        super(PollSerializer, self).post_create(obj)

    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.POLL)

        self.prepare(validated_data)
        obj = super(PollSerializer, self).create(validated_data)
        self.post_create(obj)

        return obj

    def update(self, instance, validated_data):
        self.prepare(validated_data)
        obj = super(PollSerializer, self).update(instance, validated_data)

        # clear all questions first. For some reason bulk delete is not working
        for q in instance.questions.all():
            q.delete()

        # create the questions and choices
        self.post_create(instance)

        return instance