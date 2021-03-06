from django.db import models
from base_entity.models import BaseEntityComponent, BaseEntityComponentManager
from django.contrib.auth.models import User
from polymorphic.models import PolymorphicModel, PolymorphicManager
from django.db.models import Count
from wizserver import verbs

import pdb

# Create your models here.


class PollManager(BaseEntityComponentManager):
    def owners_entities(self, user, entity_type=BaseEntityComponent.POLL):
        return super(PollManager, self).owners_entities(
            user,
            entity_type=entity_type
        )

    def users_entities(self, user, user_filter={}, entity_filter={}):
        entity_filter.update(entity_type=BaseEntityComponent.POLL)
        return super(PollManager, self).users_entities(user, user_filter=user_filter, entity_filter=entity_filter)


class Poll(BaseEntityComponent):
    description = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    num_responders = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['created']

    objects = PollManager()

    def update_state_upon_link_unlink(self):
        return True

    def question_count(self):
        return self.questions.count()


    # def num_responders(self):
    #     """
    #     how many responded to the poll
    #     """
    #     return self.userresponse_set.aggregate(
    #         num_responders=Count('id', distinct=True)
    #     ).get('num_responders')


class QuestionManager(PolymorphicManager):

    def get_choice_cls_from_type(self, question_type):
        if question_type == Question.TRUE_FALSE_CHOICE:
            c = QuestionChoicesTrueFalse
        elif question_type == Question.SCALE_OF_1_X_CHOICE:
            c = QuestionChoices1ToX
        elif question_type == Question.MULTIPLE_CHOICE:
            c = QuestionChoicesMultipleChoice
        elif question_type == Question.QUESTION_ANSWER_TEXT:
            c = QuestionChoicesText

        return c


class Question(PolymorphicModel):

    """
    Types of  question/answer within a poll - Semantics
    """
    TRUE_FALSE_CHOICE = 'TOF'
    SCALE_OF_1_X_CHOICE = 'SCL'
    MULTIPLE_CHOICE = 'MCR'
    QUESTION_ANSWER_TEXT = 'TXT'

    QUESTION_CHOICES = (
        (TRUE_FALSE_CHOICE, 'TrueFalse'),
        (SCALE_OF_1_X_CHOICE, 'ScaleOf1toX'),
        (MULTIPLE_CHOICE, 'MultipleChoiceText'),
        (QUESTION_ANSWER_TEXT, 'QuestionAnswerText')
    )

    """
    UI Types for answers
    """
    SELECT_OPTION_TYPE = 'SEL'
    GRADED_SLIDER_TYPE = 'SLD'
    RATING_TYPE = 'RTG'
    RADIO_BUTTON_TYPE = 'RAD'
    DROP_DOWN_TYPE = 'DRP'
    TEXT_AREA = 'TEX'

    UI_TYPE_CHOICES = (
        (SELECT_OPTION_TYPE, 'Select'),
        (GRADED_SLIDER_TYPE, 'GradedSlider'),
        (RADIO_BUTTON_TYPE, 'RadioButton'),
        (DROP_DOWN_TYPE, 'DropDown'),
        (TEXT_AREA, 'TextArea'),
        (RATING_TYPE, 'Rating')
    )

    USER_STATUS_RESPONDED = "responded"
    USER_STATUS_UNRESPONDED = "unresponded"

    question_type = models.CharField(
        max_length=3,
        choices=QUESTION_CHOICES,
        default=MULTIPLE_CHOICE
    )

    ui_type = models.CharField(
        max_length=3,
        choices=UI_TYPE_CHOICES,
        default=SELECT_OPTION_TYPE
    )
    created = models.DateTimeField(auto_now_add=True)

    # can user select all answers that apply ?
    single_answer = models.BooleanField(default=True)

    question = models.CharField(max_length=250, verbose_name='question')
    poll = models.ForeignKey(Poll, related_name='questions', on_delete=models.CASCADE)
    extra_text = models.BooleanField(default=False)

    num_responders = models.PositiveIntegerField(default=0)

    objects = QuestionManager()

    class Meta:
        verbose_name = 'poll'
        verbose_name_plural = 'polls'
        ordering = ['created']

    def __str__(self):
        return self.question

    def delete(self, *args, **kwargs):
        # delete questions. Some issue in django polymorphic...bulk delete is not working
        for qc in self.choices.all():
            qc.delete()

        super(Question, self).delete(*args, **kwargs)

    # def num_responders(self):
    #     return self.questions_userresponse_related.aggregate(
    #         num_responders=Count('id', distinct=True)
    #     ).get('num_responders')
    def user_state(self, user):
        if UserResponse.objects.filter(user=user, question=self).exists():
            return Question.USER_STATUS_RESPONDED

        return Question.USER_STATUS_UNRESPONDED


class QuestionChoicesBase(PolymorphicModel):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)

    def answer_stats(self):
        out = dict()
        out.update(total=UserResponse.objects.num_responses_for_question_answer(self))
        return out


class QuestionChoicesTrueFalse(QuestionChoicesBase):
    # allow user to select things like "agree/disagree", "yes, no", "true/false" etc
    true_key = models.CharField(max_length=10, default="Yes")
    false_key = models.CharField(max_length=10, default="No")

    def answer_stats(self):
        out = super(QuestionChoicesTrueFalse, self).answer_stats()

        total = self.answers_userresponse_related.count()

        t_count = self.answers_userresponse_related.filter(boolean_value=True).aggregate(
            true=Count('id', distinct=True)
        ).get('true')

        out.update(true=t_count)
        out.update(false=total - t_count)

        return out


class QuestionChoices1ToX(QuestionChoicesBase):
    low = models.IntegerField(default=0)
    high = models.IntegerField(default=10)

    def answer_stats(self):
        # AA: genius way :-) to get the stats per 1-x element
        out = super(QuestionChoices1ToX, self).answer_stats()
        [
            out.update(
                {
                    k: self.answers_userresponse_related.filter(user_value=k).aggregate(
                        count=Count('id', distinct=True)
                    ).get('count')
                }
            ) for v, k in enumerate(range(self.low, self.high+1))
        ]

        return out


class QuestionChoicesMultipleChoice(QuestionChoicesBase):
    question_key = models.CharField(max_length=1)
    question_value = models.TextField()

    def answer_stats(self):
        out = super(QuestionChoicesMultipleChoice, self).answer_stats()

        return out


class QuestionChoicesText(QuestionChoicesBase):
    def answer_stats(self):
        out = super(QuestionChoicesText, self).answer_stats()

        out.update(
            responses=self.answers_userresponse_related.all().values_list('text', flat=True)
        )

        return out


class UserResponseManager(models.Manager):

    def create(self, *args, **kwargs):
        inst = super(UserResponseManager, self).create(*args, **kwargs)

        # update number counts in polls, questions
        inst.poll.num_responders += 1
        inst.poll.save()

        inst.question.num_responders += 1
        inst.question.save()

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
        related_name="answers_%(class)s_related",
        null=True,
        blank=True
    )

    has_text = models.BooleanField(default=False)
    text = models.TextField()

    has_user_value = models.BooleanField(default=False)
    user_value = models.IntegerField(null=True, blank=True, default=5)

    has_boolean_value = models.BooleanField(default=False)
    boolean_value = models.BooleanField(default=True)

    response_time = models.DateTimeField(auto_now=True)

    objects = UserResponseManager()

