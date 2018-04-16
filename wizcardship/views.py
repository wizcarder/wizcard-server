"""
.. autofunction:: wizconnection_request

.. autofunction:: wizconnection_accept

.. autofunction:: wizconnection_decline

.. autofunction:: wizconnection_cancel

.. autofunction:: wizconnection_delete

.. autofunction:: user_block

.. autofunction:: user_unblock

from django.http import HttpResponseBadRequest, Http404
from django.http import HttpResponse
from django.db import transaction
from django.views.generic.base import RedirectView
from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from models import WizConnectionRequest, Wizcard
from app_settings import REDIRECT_FALLBACK_TO_PROFILE

class BaseWizcardActionView(RedirectView):
    http_method_names = ['get', 'post']
    permanent = False

    def set_url(self, request, **kwargs):
        if 'redirect_to' in kwargs:
            self.url = kwargs['redirect_to']
        elif 'redirect_to_param' in kwargs and \
                                kwargs['redirect_to_param'] in request.REQUEST:
            self.url = request.REQUEST[kwargs['redirect_to_param']]
        elif 'redirect_to' in request.REQUEST:
            self.url = request.REQUEST['next']
        elif REDIRECT_FALLBACK_TO_PROFILE:
            self.url = request.user.get_profile().get_absolute_url()
        else:
            self.url = request.META.get('HTTP_REFERER', '/')

    def get(self, request, username, *args, **kwargs):
        if request.user.username == username:
            return HttpResponseBadRequest(ugettext(u'You can\'t becard ' \
                                                   u'yourself.'))
        user = get_object_or_404(User, username=username)
        self.action(request, user, *args, **kwargs)
        self.set_url(request, **kwargs)
        return super(BaseWizcardActionView, self).get(request, **kwargs)


class WizcardAcceptView(BaseWizcardActionView):
    @transaction.commit_on_success
    def accept_wizconnection(self, from_user, to_user):
        get_object_or_404(WizConnectionRequest,
                          from_user=from_user,
                          to_user=to_user).accept()

    def action(self, request, user, **kwargs):
        self.accept_wizconnection(user, request.user)


class WizConnectionRequestView(WizcardAcceptView):
    @transaction.commit_on_success
    def action(self, request, user, **kwargs):
        if Wizcard.objects.are_wizconnections(request.user, user):
            raise RuntimeError('%r amd %r are already wizconnections' % \
                                                          (request.user, user))
        try:
            # If there's a wizconnection request from the other user accept it.
            self.accept_wizconnection(user, request.user)
        except Http404:
            request_message = request.REQUEST.get('message', u'')
            # If we already have an active wizconnection request IntegrityError
            # will be raised and the transaction will be rolled back.
            WizConnectionRequest.objects.create(from_user=request.user,
                                             to_user=user,
                                             message=request_message)


class WizcardDeclineView(BaseWizcardActionView):
    def action(self, request, user, **kwargs):
        get_object_or_404(WizConnectionRequest,
                          from_user=user,
                          to_user=request.user).decline()


class WizcardCancelView(BaseWizcardActionView):
    def action(self, request, user, **kwargs):
        get_object_or_404(WizConnectionRequest,
                          from_user=request.user,
                          to_user=user).cancel()


class WizcardDeleteView(BaseWizcardActionView):
    def action(self, request, user, **kwargs):
        Wizcard.objects.uncard(request.user, user)


class WizcardBlockView(BaseWizcardActionView):
    def action(self, request, user, **kwargs):
        request.user.user_blocks.blocks.add(user)


class WizcardUnblockView(BaseWizcardActionView):
    def action(self, request, user, **kwargs):
        request.user.user_blocks.blocks.remove(user)


wizconnection_request = login_required(WizConnectionRequestView.as_view())
wizconnection_accept = login_required(WizcardAcceptView.as_view())
wizconnection_decline = login_required(WizcardDeclineView.as_view())
wizconnection_cancel = login_required(WizcardCancelView.as_view())
wizconnection_delete = login_required(WizcardDeleteView.as_view())
user_block = login_required(WizcardBlockView.as_view())
user_unblock = login_required(WizcardUnblockView.as_view())
"""


from rest_framework import viewsets
from rest_framework.response import Response
from wizcardship.models import Wizcard
from wizcardship.serializers import WizcardSerializer

# Create your views here.


class WizcardViewSet(viewsets.ModelViewSet):

    serializer_class = WizcardSerializer
    queryset = Wizcard.objects.all()

    def retrieve(self, request, pk=None):
        queryset = Wizcard.objects.get(id=pk)
        serializer = WizcardSerializer(queryset)
        return Response(serializer.data)

from django_filters import rest_framework as filters

class WizcardQueryFilter(filters.FilterSet):

    username = filters.CharFilter(name="user__username")

    class Meta:
        model = Wizcard
        fields = ['username']

class WizcardUserExistsView(viewsets.ModelViewSet):

    serializer_class = WizcardSerializer
    queryset = Wizcard.objects.all()
    filter_class = WizcardQueryFilter
    filter_backend = (filters.DjangoFilterBackend,)

