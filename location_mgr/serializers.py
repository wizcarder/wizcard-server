__author__ = 'aammundi'

from rest_framework import serializers
from location_mgr.models import LocationMgr
import pdb


class LocationSerializerField(serializers.ModelSerializer):
    class Meta:
        model = LocationMgr
        fields = ('lat', 'lng')

    def get_queryset(self):
        pass

    def to_representation(self, value):
        out = dict()
        if value.exists():
            out['lat'] = float(value.get().lat)
            out['lng'] = float(value.get().lng)

        return out