__author__ = 'aammundi'

from rest_framework import serializers
from polls.models import Poll, Question, QuestionChoicesBase
from base_entity.models import BaseEntityComponent
from entity.serializers import EntitySerializer
from django.contrib.contenttypes.models import ContentType
from entity.serializers import EventSerializerL0

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

    @staticmethod
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


# this is used to create a poll. This is also used to send serialized Poll to App
class PollSerializer(EntitySerializer):
    class Meta:
        model = Poll
        fields = ('id', 'description', 'questions', 'state')

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
        super(PollSerializer, self).update(instance, validated_data)

        # clear all questions first. For some reason bulk delete is not working
        for q in instance.questions.all():
            q.delete()

        # create the questions and choices
        self.post_create(instance)

        return instance


class PollResponseSerializer(EntitySerializer):
    class Meta:
        model = Poll
        fields = ('id', 'event', 'num_responders', 'description', 'questions', 'state')

    questions = QuestionResponseSerializer(many=True)
    event = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_event(self, obj):
        # typically expecting one parent only...the Poll UI allows associating with one event only. No issues
        # if extended to multiple events both in the related_to plumbing and here as well. Here, since we're
        # passing the whole list, the only difference is that even for a single case, there will be {[]] instead
        # of {}, in the response
        event = obj.get_parent_entities_by_contenttype_id(ContentType.objects.get(model="event"))
        return EventSerializerL0(event, many=True).data



