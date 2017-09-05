from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from taganomy.models import Taganomy
from taganomy.serializers import TaganomySerializer
from django.http import Http404
from rest_framework.decorators import detail_route
from rest_framework import status

# Create your views here.
class TaganomyViewSet(viewsets.ModelViewSet):
    queryset = Taganomy.objects.all()
    serializer_class = TaganomySerializer
