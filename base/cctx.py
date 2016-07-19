from django.contrib.contenttypes.models import ContentType
from wizserver import verbs
from lib import wizlib
from wizserver import fields
from lib.preserialize.serialize import serialize



class ConnectionContext(object):
    def __repr__(self):
        return self.description

    def __init__(self, asset_obj=None, connection_mode=None, description=None, location=""):
        asset_type = ContentType.objects.get_for_model(asset_obj).name if asset_obj else None
        self._cctx = dict(
            asset_obj=asset_obj,
            asset_type=asset_type,
            connection_mode=connection_mode,
            description=description,
            location=location
        )



    @property
    def context(self):
        return self._cctx

    @property
    def asset_type(self):
        return self.context['asset_type']

    @property
    def connection_mode(self):
        return self.context['connection_mode']

    @property
    def object(self):
        return self.context['asset_obj']

    @property
    def asset_id(self):
        return self.object.pk

    @property
    def description(self):
        return self.context['description']

    @property
    def location(self):
        return self.context['location']

    @description.setter
    def description(self, text):
        self._cctx['description'] = text

    @location.setter
    def location(self, location):
        self._cctx['location'] = location

    def describe(self):
        if self.asset_type == ContentType.objects.get(model="wizcard").name:
            if self.connection_mode in [verbs.INVITE_VERBS[verbs.WIZCARD_CONNECT_T],
                                        verbs.INVITE_VERBS[verbs.WIZCARD_CONNECT_U]]:
                try:
                    self.description = "via wizcard exchange {}".format(wizlib.format_location_name(self.location))
                except:
                    self.description = "via wizcard exchange"
            elif self.connection_mode == verbs.INVITE_VERBS[verbs.WIZCARD_INVITE]:
                self.description = "via WizCard Invite"
            elif self.connection_mode == verbs.INVITE_VERBS[verbs.EMAIL_INVITE]:
                self.description = "via Email Invite"
            elif self.connection_mode == verbs.INVITE_VERBS[verbs.SMS_INVITE]:
                self.description = "via SMS Invite"
            else:
                self.description = wizlib.format_location_name(self.location)
        elif self.asset_type == ContentType.objects.get(model="virtualtable").name:
            self.description = "via round table {}".format(self.object)
        elif self.asset_type == ContentType.objects.get(model="wizcardflick").name:
            self.description = "via flick pick @{}".format(self.object.reverse_geo_name)
        elif self.asset_type == ContentType.objects.get(model="meishi").name:
            self.description = "via meishi"


class NotifContext(object):
    def __init__(self, description, asset_id=None, asset_type=None, connection_mode=None, timestamp=None):
        self._out = dict(
            asset_id=asset_id,
            asset_type=asset_type,
            description=description,
            mode=connection_mode,
            time=timestamp
        )

    def __repr__(self):
        return self._out['description']

    @property
    def context(self):
        return self._out

    @property
    def id(self):
        return self._out['asset_id']

    @id.setter
    def id(self, aid):
        self._out['asset_id'] = aid

    # @key_val.setter
    def key_val(self, key, val):
        self._out[key] = val
