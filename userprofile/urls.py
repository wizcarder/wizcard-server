__author__ = 'aammundi'
from userprofile.views import UserViewSet, ProfileView
from rest_framework.routers import DefaultRouter
from django.conf.urls import patterns, include, url
from rest_auth.views import LoginView, LogoutView


router = DefaultRouter()
router.register(r'users', UserViewSet, base_name='users')

urlpatterns = router.urls

urlpatterns = [

#    url(r'^account-confirm-email/(?P<key>\w+)/$', allauthemailconfirmation, name="account_confirm_email"),
    url(r'^registration/', include('rest_auth.registration.urls')),
    url(r'^login/$', LoginView.as_view(), name='rest_login'),
    url(r'^logout/$', LogoutView.as_view(), name='rest_logout'),
    url(r'^profile/$', ProfileView.as_view(), name='profile')
#    url(r'^password/', LogoutView.as_view(), name='rest_logout'),
#    url(r'^logout/', include('rest_auth.urls')),
#   # url(r'^rest-auth/facebook/$', FacebookLogin.as_view(), name='fb_login')
]

