from django.db import models
from base_entity.models import BaseEntityComponent, BaseEntityComponentManager
from django.contrib.auth.models import User
from polymorphic.models import PolymorphicModel


# Create your models here.

class PollManager(BaseEntityComponentManager):
    def owners_entities(self, user, entity_type=BaseEntityComponent.POLL):
        return super(PollManager, self).owners_entities(
            user,
            entity_type=entity_type
        )

    def users_entities(self, user, entity_type=BaseEntityComponent.CAMPAIGN):
        return super(PollManager, self).users_entities(
            user,
            entity_type=entity_type
        )


class Poll(BaseEntityComponent):
    description = models.CharField(max_length=100)
    is_published = models.BooleanField(default=True, verbose_name='is published')

    objects = PollManager()

    def question_count(self):
        return self.question_set.count()

    def num_responders(self):
        return self.responders.count()

    def get_num_responses(self):
        return self.question_set.count()

    """
    detailed response breakdown of the Poll
    """
    def get_poll_responses(self):
        return None


class Question(PolymorphicModel):

    """
    Types of Poll question/answer - Semantics
    """
    MULTIPLE_TEXT_CHOICE = 'MCT'
    SCALE_OF_1_X_CHOICE = 'SCL'
    ABCD_CHOICE = 'MCR'
    TRUE_FALSE_CHOICE = 'TOF'

    QUESTION_CHOICES = (
        (MULTIPLE_TEXT_CHOICE, 'MultipleChoiceText'),
        (SCALE_OF_1_X_CHOICE, 'ScaleOf1toX'),
        (ABCD_CHOICE, 'ChoiceAbcd'),
        (TRUE_FALSE_CHOICE, 'TrueFalse'),
    )

    """
    UI Types for answers
    """
    SELECT_OPTION_TYPE = 'SEL'
    GRADED_SLIDER_TYPE = 'SLD'
    RADIO_BUTTON_TYPE = 'RAD'
    DROP_DOWN_TYPE = 'DRP'

    UI_TYPE_CHOICES = (
        (SELECT_OPTION_TYPE, 'Select'),
        (GRADED_SLIDER_TYPE, 'GradedSlider'),
        (RADIO_BUTTON_TYPE, 'RadioButton'),
        (DROP_DOWN_TYPE, 'DropDown'),
    )

    question_type = models.CharField(
        max_length=3,
        choices=QUESTION_CHOICES,
        default=MULTIPLE_TEXT_CHOICE
    )

    ui_type = models.CharField(
        max_length=3,
        choices=UI_TYPE_CHOICES,
        default=SELECT_OPTION_TYPE
    )

    # can user select all answers that apply ?
    single_answer = models.BooleanField(default=True)

    question = models.CharField(max_length=250, verbose_name='question')
    poll = models.ForeignKey(Poll, related_name='questions', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'poll'
        verbose_name_plural = 'polls'

    def __str__(self):
        return self.question

    @classmethod
    def get_choice_cls_from_type(cls, question_type):
        if question_type == cls.MULTIPLE_TEXT_CHOICE:
            return QuestionChoicesText
        elif question_type == cls.SCALE_OF_1_X_CHOICE:
            return QuestionChoices1ToX
        else:
            return QuestionChoicesBase


class QuestionChoicesBase(PolymorphicModel):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    extra_text = models.BooleanField(default=False)


class QuestionChoicesText(QuestionChoicesBase):
    question_key = models.CharField(max_length=1)
    question_value = models.TextField()


class QuestionChoices1ToX(QuestionChoicesBase):
    low = models.IntegerField(default=0)
    high = models.IntegerField(default=10)


class UserAnswerManager(models.Manager):

    """
    how many responded to the poll
    """
    def num_respondents(self, poll):
        return poll.user_answer_set.count()


class UserResponse(models.Model):
    # the question that was answered
    question = models.ForeignKey(Question)
    # answer that was given
    answer = models.ForeignKey(QuestionChoicesBase)

    has_extra_text = models.BooleanField(default=False)
    extra_text = models.TextField()

    has_user_value = models.BooleanField(default=False)
    user_value = models.IntegerField(blank=True)

    object = UserAnswerManager()

