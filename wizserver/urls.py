from django.conf.urls.defaults import patterns, url


urlpatterns = patterns(
    'wizserver.views',
    url(r'^$', 'wizrequest_handler')
)
