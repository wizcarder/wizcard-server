__author__ = 'aammundi'
from django.dispatch import Signal
user_type_created = Signal(providing_args=['user_type'])