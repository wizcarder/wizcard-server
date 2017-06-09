__author__ = 'aammundi'
from userprofile.views import UserViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'users', UserViewSet, base_name='users')

urlpatterns = router.urls
