__author__ = 'aammundi'

from rest_framework import serializers
from polls.models import Poll, Question, QuestionChoicesBase
from base_entity.models import BaseEntityComponent
from entity.serializers import EntitySerializer

import pdb

class QuestionChoicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionChoicesBase
        fields = ('extra_text', 'question_key', 'question_value', 'low', 'high')

    question_key = serializers.CharField(required=False)
    question_value = serializers.CharField(required=False)
    low = serializers.CharField(required=False)
    high = serializers.CharField(required=False)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('question_type', 'ui_type', 'single_answer', 'question', 'poll', 'choices')

    choices = QuestionChoicesSerializer(many=True)
    poll = serializers.PrimaryKeyRelatedField(read_only=True)


class PollSerializer(EntitySerializer):
    class Meta:
        model = Poll
        fields = ('description', 'questions')

    questions = QuestionSerializer(many=True)

    def prepare(self, validated_data):
        self.questions = validated_data.pop('questions', None)

    def post_create(self, obj):
        for q in self.questions:
            choices = q.pop('choices', [])
            q_inst = Question.objects.create(poll=obj, **q)

            for c in choices:
                cls = Question.get_choice_cls_from_type(q['question_type'])
                cls.objects.create(question=q_inst, **c)

    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.POLL)

        self.prepare(validated_data)
        obj = super(PollSerializer, self).create(validated_data)
        self.post_create(obj)

        return obj

    def update(self, instance, validated_data):
        instance = super(PollSerializer, self).update(instance, validated_data)

        return instance