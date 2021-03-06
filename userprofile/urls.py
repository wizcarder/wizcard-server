__author__ = 'aammundi'
from userprofile.views import UserViewSet, CustomObtainAuthToken
from rest_framework.routers import DefaultRouter
from django.conf.urls import include, url
from rest_auth.views import  LogoutView, UserDetailsView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView


router = DefaultRouter()
router.register(r'users', UserViewSet, base_name='users')

urlpatterns = router.urls

urlpatterns += [

#    url(r'^account-confirm-email/(?P<key>\w+)/$', allauthemailconfirmation, name="account_confirm_email"),
    url(r'^registration/', include('rest_auth.registration.urls')),
    url(r'^login/$', CustomObtainAuthToken.as_view(), name='user_login'),
    url(r'^reset-passwd', PasswordResetView.as_view(), name='reset-passwd'),
    url(r'^change-passwd', PasswordChangeView.as_view(), name='change-passwd'),
    url(r'^reset-passwd-confirm', PasswordResetConfirmView.as_view(), name='reset-passwd-confirm'),
    url(r'^logout/$', LogoutView.as_view(), name='rest_logout'),
    #url(r'^profile/$', ProfileView.as_view(), name='profile')
    url(r'^profile/$', UserDetailsView.as_view(), name='profile')
#    url(r'^password/', LogoutView.as_view(), name='rest_logout'),
#    url(r'^logout/', include('rest_auth.urls')),
#   # url(r'^rest-auth/facebook/$', FacebookLogin.as_view(), name='fb_login')
]

