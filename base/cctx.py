from django.contrib.contenttypes.models import ContentType
class ConnectionContext(object):
    def __init__(self, asset_obj=None, connection_mode=None, description=None):
        asset_type = ContentType.objects.get_for_model(asset_obj).name if asset_obj else None
        self._cctx = dict(
                asset_obj=asset_obj,
                asset_type=asset_type,
                connection_mode=connection_mode,
                description=""
                )
        self.describe()
    @property
    def context(self):
        return self._cctx

    @property
    def asset_type(self):
        return self.context['asset_type']

    @property
    def object(self):
        return self.context['asset_obj']

    @property
    def asset_id(self):
        return self.object.pk

    @property
    def description(self):
        return self.context['description']

    @description.setter
    def description(self, text):
        self._cctx['description'] = text

    def describe(self):
        if self.asset_type == ContentType.objects.get(model="wizcard").name:
            self.description = "via wizcard exchange"
        elif self.asset_type == ContentType.objects.get(model="virtualtable").name:
            self.description = "via round table {}".format(self.object)
        elif self.asset_type == ContentType.objects.get(model="wizcardflick").name:
            self.description = "via flick pick @{}".format(self.object.reverse_geo_name)
        elif self.asset_type == ContentType.objects.get(model="meishi").name:
            self.description = "via meishi"

class NotifContext(object):
    def __init__(self, description, asset_id=None, asset_type=None):
        self._out = dict(
                asset_id=asset_id,
                asset_type=asset_type,
                description=description
                )

    @property
    def context(self):
        return self._out

    @property
    def id(self):
        return self._out['asset_id']

    @id.setter
    def id(self, id):
        self._out['asset_id'] = id

#    @property
#    def key_val(self, key):
#        return self._out['key']
    
#    @key_val.setter
    def key_val(self, key, val):
        self._out[key] = val