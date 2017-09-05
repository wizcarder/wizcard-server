__author__ = 'aammundi'
from django.dispatch import Signal

media_create = Signal(providing_args=['objs'])
