from django.db import models
from django.db import models
import datetime
from lib.pytrie import SortedStringTrie as trie
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from location_mgr.signals import location
from django.db.models.signals import pre_delete
from lib import wizlib
import random
import pdb

class LocationMgrManager(models.Manager):
    def lookup_by_key(self, tree, key, n):
        print 'current tree [{tree}]'.format (tree=tree)
        result, count = wizlib.lookup_by_key(tree=tree, key=key, num_results=n)
        print 'looking up  gives result [{result}]'.format (result=result)
        return result, count

    def lookup_by_lat_lng(self, tree, lat, lng, n):
        if not tree:
            return None, None
        key = wizlib.create_geohash(lat, lng)
        return self.lookup_by_key(key, tree, n, False)


class LocationMgr(models.Model):
    lat = models.FloatField(null=True, default=None)
    lng = models.FloatField(null=True, default=None)
    key = models.CharField(null=True, max_length=100)
    lastseen = models.DateTimeField(default=datetime.datetime.now,
                                    editable=False)

    #GenericForeignKey to LocationMgr
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    objects = LocationMgrManager()

    def do_update(self, lat, lng, tree):
        update = False
        update_object = None
        if self.lat != lat:
            self.lat = lat
            update = True
        if self.lng != lng:
            self.lng = lng
            update = True
        if update:
            self.delete_key(tree)
            newkey = wizlib.create_geohash(self.lat, self.lng)
            self.key = newkey
            self.save()
            tree[newkey] = self.pk
            update_object = self
        elif not tree.has_key(self.key):
            tree[self.key] = self.pk
        
        print 'current tree [{tree}]'.format (tree=tree)
        return update, update_object

    def delete_key(self, tree):
        try:
            del tree[self.key]
        except:
            pass
        print 'current tree [{tree}]'.format (tree=tree)

def location_update_handler(**kwargs):
    kwargs.pop('signal', None)
    sender = kwargs.pop('sender')
    lat = kwargs.pop('lat')
    lng = kwargs.pop('lng')
    key = kwargs.pop('key', None)
    tree = kwargs.pop('tree')

    newlocation = LocationMgr(
        lat=lat,
        lng=lng,
        key=key,
        content_type=ContentType.objects.get_for_model(sender),
        object_id=sender.pk)

    newlocation.save()
    #update tree
    tree[key] = sender.pk
    print 'current tree [{tree}]'.format (tree=tree)
    return newlocation

location.connect(location_update_handler, dispatch_uid='location_mgr.models.location_mgr')



