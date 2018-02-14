__author__ = 'aammundi'

from rest_framework import serializers
from polls.models import Question, UserResponse
from polls.models import QuestionChoicesBase

import pdb


class QuestionChoicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionChoicesBase
        fields = ('id', 'question_key', 'question_value', 'low', 'high', 'true_key', 'false_key',)

    question_key = serializers.CharField(required=False)
    question_value = serializers.CharField(required=False)
    low = serializers.CharField(required=False)
    high = serializers.CharField(required=False)
    true_key = serializers.CharField(required=False)
    false_key = serializers.CharField(required=False)

# put in all this...however, don't have a way yet to dynamically set the
# serializer based on the incoming question_type

# class QuestionChoicesSerializerBase(serializers.ModelSerializer):
#     class Meta:
#         model = QuestionChoicesBase
#         fields = ('id',)
#
#
# class QuestionChoicesSerializerTrueOrFalse(QuestionChoicesSerializerBase):
#     class Meta:
#         model = QuestionChoicesTrueFalse
#         my_fields = ('true_key', 'false_key')
#         fields = QuestionChoicesSerializerBase.Meta.fields + my_fields
#
#
# class QuestionChoicesSerializerText(QuestionChoicesSerializerBase):
#     class Meta:
#         model = QuestionChoicesText
#         fields = QuestionChoicesSerializerBase.Meta.fields
#
#
# class QuestionChoicesSerializer1ToX(QuestionChoicesSerializerBase):
#     class Meta:
#         model = QuestionChoices1ToX
#         my_fields = ('low', 'high',)
#
#         fields = QuestionChoicesSerializerBase.Meta.fields + my_fields
#
#     low = serializers.CharField(required=False)
#     high = serializers.CharField(required=False)
#
#
# class QuestionChoicesSerializerMultipleChoice(QuestionChoicesSerializerBase):
#     class Meta:
#         model = QuestionChoicesMultipleChoice
#         my_fields = ('quesion_key', 'question_value',)
#         fields = QuestionChoicesSerializerBase.Meta.fields + my_fields
#
#     question_key = serializers.CharField(required=False)
#     question_value = serializers.CharField(required=False)


class QuestionChoicesResponseSerializer(QuestionChoicesSerializer):
    class Meta:
        model = QuestionChoicesBase
        my_fields = ('answers',)
        fields = QuestionChoicesSerializer.Meta.fields + my_fields

    answers = serializers.SerializerMethodField(read_only=True)

    def get_answers(self, obj):
        return obj.answer_stats()


class QuestionSerializerL1(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'num_responders',)
        read_only_fields = ('num_responders',)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'question_type', 'ui_type', 'single_answer', 'extra_text',
                  'question', 'poll', 'choices', 'num_responders', 'user_state',)
        read_only_fields = ('num_responders',)

    choices = QuestionChoicesSerializer(many=True)
    poll = serializers.PrimaryKeyRelatedField(read_only=True)

    # not elegant. Have to do this since:
    # 1. This is not inheriting from EntitySerializer
    # 2. Both app and portal are using the same
    user_state = serializers.SerializerMethodField()

    def get_user_state(self, obj):
        return obj.user_state(self.context.get('user', None))

    def update(self, instance, validated_data):
        choices = validated_data.pop('choices', [])

        # clear all choices
        instance.choices.all().delete()

        cls = Question.objects.get_choice_cls_from_type(validated_data['question_type'])
        [cls.objects.create(question=instance, **c) for c in choices]

        obj = super(QuestionSerializer, self).update(instance, validated_data)

        return obj


class QuestionResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'question_type', 'question', 'choices', 'num_responders', 'ui_type')
        read_only_fields = ('num_responders',)

    choices = QuestionChoicesResponseSerializer(many=True)


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResponse
        fields = ('text',)
