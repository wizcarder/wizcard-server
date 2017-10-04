__author__ = 'aammundi'

from django.conf.urls import url, include, patterns
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers
from polls.views import PollViewSet

poll_router = SimpleRouter()
poll_router.register(r'polls', PollViewSet, base_name='polls')


urlpatterns = patterns(
    '',
    url(r'^', include(poll_router.urls)),
)