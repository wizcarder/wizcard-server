__author__ = 'aammundi'
from speaker.views import SpeakerViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'speaker', SpeakerViewSet, base_name='speaker')

urlpatterns = router.urls
