from django.contrib.contenttypes.models import ContentType
class ConnectionContext(object):
    def __init__(self, asset_obj=None, connection_mode=None, description=None):

        asset_type = ContentType.objects.get_for_model(asset_obj) if asset_obj else None
        self._cctx = dict(
                asset_obj=asset_obj,
                asset_type=asset_type,
                connection_mode=connection_mode,
                description=""
                )

    @property
    def context(self):
        return self._cctx

    @property
    def object(self):
        return self.context['asset_obj']

    @property
    def description(self):
        return self.context['description']

    @description.setter
    def description(self, text):
        self._cctx['description'] = text

    def describe(self):
        self.description = "This is a test description"
        return self.description

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
