from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import generics
from email_and_push_infra.models import EmailAndPush, EmailEvent
from email_and_push_infra.serializers import EmailPushSerializer
from django.http import Http404
import pdb

# Create your views here.
class EmailAndPushViewSet(viewsets.ModelViewSet):
    """This view provides list, detail, create, retrieve, update
    and destroy actions for Things."""
    model = EmailAndPush
    serializer_class = EmailPushSerializer
