__author__ = 'aammundi'

from django.conf.urls import url, include, patterns
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers
from polls.views import PollViewSet, PollQuestionViewSet, PollQuestionChoicesViewSet, PollAnswersViewSet

poll_router = SimpleRouter()
poll_router.register(r'polls', PollViewSet, base_name='polls')
questions_router = routers.NestedSimpleRouter(poll_router, r'polls', lookup='poll')
questions_router.register(r'question', PollQuestionViewSet, base_name='poll-question')
choices_router = routers.NestedSimpleRouter(questions_router, r'question', lookup='question')
choices_router.register(r'choice', PollQuestionChoicesViewSet, base_name='question-choices')
answers_router = routers.NestedSimpleRouter(poll_router, r'polls', lookup='poll')
answers_router.register(r'answers', PollAnswersViewSet, base_name='poll-answers')

urlpatterns = patterns(
    '',
    url(r'^', include(poll_router.urls)),
    url(r'^', include(questions_router.urls)),
    url(r'^', include(choices_router.urls)),
    url(r'^', include(answers_router.urls)),

)
