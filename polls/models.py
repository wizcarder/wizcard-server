from django.db import models
from base_entity.models import BaseEntityComponent, BaseEntityComponentManager
from django.contrib.auth.models import User
from polymorphic.models import PolymorphicModel
from django.db.models import Count

import pdb

# Create your models here.


class PollManager(BaseEntityComponentManager):
    def owners_entities(self, user, entity_type=BaseEntityComponent.POLL):
        return super(PollManager, self).owners_entities(
            user,
            entity_type=entity_type
        )

    def users_entities(self, user, **kwargs):
        kwargs.update(entity_type=BaseEntityComponent.POLL)
        return super(PollManager, self).users_entities(
            user,
            **kwargs
        )


class Poll(BaseEntityComponent):
    POLL_STATE_UNPUBLISHED = 'UNP'
    POLL_STATE_ACTIVE = 'ACT'
    POLL_STATE_EXPIRED = 'EXP'

    POLL_STATE_CHOICES = (
        (POLL_STATE_UNPUBLISHED, 'unpublished'),
        (POLL_STATE_ACTIVE, 'active'),
        (POLL_STATE_EXPIRED, 'expired')
    )

    description = models.CharField(max_length=100)
    state = models.CharField(choices=POLL_STATE_CHOICES, default=POLL_STATE_UNPUBLISHED, max_length=3)
    created = models.DateTimeField(auto_now_add=True)

    objects = PollManager()

    def delete(self, *args, **kwargs):
        # delete questions. Some issue in django polymorphic...bulk delete is not working
        for q in self.questions.all():
            q.delete()

        super(Poll, self).delete(*args, **kwargs)

    def question_count(self):
        return self.questions.count()

    def num_responders(self):
        """
        how many responded to the poll
        """
        return self.userresponse_set.aggregate(
            num_responders=Count('user', distinct=True)
        ).get('num_responders')

    def set_state(self, state):
        self.state = state
        self.save()


class Question(PolymorphicModel):

    """
    Types of  question/answer within a poll - Semantics
    """
    MULTIPLE_TEXT_CHOICE = 'MCT'
    SCALE_OF_1_X_CHOICE = 'SCL'
    ABCD_CHOICE = 'MCR'
    TRUE_FALSE_CHOICE = 'TOF'
    QUESTION_ANSWER = 'QA'

    QUESTION_CHOICES = (
        (MULTIPLE_TEXT_CHOICE, 'MultipleChoiceText'),
        (SCALE_OF_1_X_CHOICE, 'ScaleOf1toX'),
        (ABCD_CHOICE, 'ChoiceAbcd'),
        (TRUE_FALSE_CHOICE, 'TrueFalse'),
        (QUESTION_ANSWER, 'QuestionAnswer')
    )

    """
    UI Types for answers
    """
    SELECT_OPTION_TYPE = 'SEL'
    GRADED_SLIDER_TYPE = 'SLD'
    RADIO_BUTTON_TYPE = 'RAD'
    DROP_DOWN_TYPE = 'DRP'
    TEXT_AREA = 'TEX'

    UI_TYPE_CHOICES = (
        (SELECT_OPTION_TYPE, 'Select'),
        (GRADED_SLIDER_TYPE, 'GradedSlider'),
        (RADIO_BUTTON_TYPE, 'RadioButton'),
        (DROP_DOWN_TYPE, 'DropDown'),
        (TEXT_AREA, 'TextArea')
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

    def delete(self, *args, **kwargs):
        # delete questions. Some issue in django polymorphic...bulk delete is not working
        for qc in self.choices.all():
            qc.delete()

        super(Question, self).delete(*args, **kwargs)

    def answer_stats(self):
        out = dict()
        out.update(total=UserResponse.objects.num_responses_for_question(self))
        return out


class QuestionChoicesBase(PolymorphicModel):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    extra_text = models.BooleanField(default=False)

    def answer_stats(self):
        out = dict()
        out.update(total=UserResponse.objects.num_responses_for_question_answer(self))
        return out


class QuestionChoicesText(QuestionChoicesBase):
    question_key = models.CharField(max_length=1)
    question_value = models.TextField()


class QuestionChoices1ToX(QuestionChoicesBase):
    low = models.IntegerField(default=0)
    high = models.IntegerField(default=10)


class UserResponseManager(models.Manager):
    def num_responses_for_question(self, question):
        return self.filter(question=question).count()

    def num_responses_for_question_answer(self, answer):
        return self.filter(answer=answer).count()


class UserResponse(models.Model):
    # user answering the poll
    user = models.ForeignKey(User, db_index=True)

    # poll that was taken
    poll = models.ForeignKey(Poll, db_index=True)
    # the question that was answered
    question = models.ForeignKey(
        Question,
        related_name="questions_%(class)s_related"
    )
    # answer that was given
    answer = models.ForeignKey(
        QuestionChoicesBase,
        related_name="answers_%(class)s_related"
    )

    has_extra_text = models.BooleanField(default=False)
    extra_text = models.TextField()

    has_user_value = models.BooleanField(default=False)
    user_value = models.IntegerField(blank=True, default=5)

    response_time = models.DateTimeField(auto_now=True)

    objects = UserResponseManager()