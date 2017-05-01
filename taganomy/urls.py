
from django.conf.urls import url, include, patterns
from taganomy.views import TaganomyViewSet
from rest_framework_nested import routers
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'taganomy', TaganomyViewSet, base_name='taganomy')


urlpatterns = patterns(
    '',
    url(r'^', include(router.urls)),
)
