__author__ = 'aammundi'

from rest_framework import serializers
from polls.models import Poll, Question, QuestionChoicesBase

import pdb


class QuestionChoicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionChoicesBase
        fields = ('id', 'extra_text', 'question_key', 'question_value', 'low', 'high')

    question_key = serializers.CharField(required=False)
    question_value = serializers.CharField(required=False)
    low = serializers.CharField(required=False)
    high = serializers.CharField(required=False)


class QuestionChoicesResponseSerializer(QuestionChoicesSerializer):
    class Meta:
        model = QuestionChoicesBase
        my_fields = ('answers',)
        fields = QuestionChoicesSerializer.Meta.fields + my_fields

    answers = serializers.SerializerMethodField(read_only=True)

    def get_answers(self, obj):
        return obj.answer_stats()


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
            cls.objects.create(question=instance, **c)

        obj = super(QuestionSerializer, self).update(instance, validated_data)

        return obj


class QuestionResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'question_type', 'question', 'choices')

    choices = QuestionChoicesResponseSerializer(many=True)