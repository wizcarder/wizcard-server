from django.db import models
import datetime
from lib.pytrie import SortedStringTrie as trie
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from location_mgr.signals import location
from django.db.models.signals import pre_delete
from lib import wizlib
import threading
import random
import pdb

ptree = trie()
wtree = trie()
vtree = trie()

class LocationMgrManager(models.Manager):

    PTREE = 1 
    WTREE = 2
    VTREE = 3

    location_tree_handles = {
        PTREE : ptree,
        WTREE : wtree,
        VTREE : vtree
    }

    def get_tree_from_type(self, type):
	return self.location_tree_handles[type]
  
    def get_tree_from_content_type(self, type):
	#AA_TODO
	return PTREE

    def lookup_by_key(self, tree_type, key, n, key_in_tree=True):
	tree = self.get_tree_from_type(tree_type)
        print 'current tree [{tree}]'.format (tree=tree)
        result, count = wizlib.lookup_by_key(key, 
                                             tree, 
                                             n,
                                             key_in_tree)
        print 'looking up  gives result [{result}]'.format (result=result)
        return result, count

    def lookup_by_lat_lng(self, tree_type, lat, lng, n):
        key = wizlib.create_geohash(lat, lng)
        return self.lookup_by_key(tree_type, key, n, False)


class LocationMgr(models.Model):
    lat = models.FloatField(null=True, default=None)
    lng = models.FloatField(null=True, default=None)
    key = models.CharField(null=True, max_length=100)

    #GenericForeignKey to objects requiring locationMgr services
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    objects = LocationMgrManager()

    def do_update(self, lat, lng, tree_type):
	tree = LocationMgr.objects.get_tree_from_type(tree_type)
        update = False
        update_object = None
        object_id = self.object_id
        if self.lat != lat:
            self.lat = lat
            update = True
        if self.lng != lng:
            self.lng = lng
            update = True
        if update:
            try:
                #delete old guy
                wizlib.delete_key(self.key, tree)
            except:
                #can happen when server is restarted
                pass
            #add new guy
            newkey = wizlib.create_geohash(self.lat, self.lng)
            self.key = newkey
            self.save()
            #update tree with new key (and old id)
            tree[newkey] = object_id
            update_object = self
        elif not tree.has_key(self.key):
            tree[self.key] = object_id
        
        print 'current tree [{tree}]'.format (tree=tree)
        return update, update_object

    def expire(self):
	try:
            tree = LocationMgr.objects.get_tree_from_content_type(self.content_type)
	    wizlib.delete_key(self.key, tree)
	except:
	    print '!!!key {key} not found in tree'.format (key=key)
	self.delete()

    def delete_key_from_tree(self, tree_type):
            wizlib.delete_key(
                    LocationMgr.objects.get_tree_from_type(tree_type),
                    self.key)

    def delete(self, *args, **kwargs):
        #AA_TODO: move above function here once treey_type usage 
        #is not  required
        super(VirtualTable, self).delete(*args, **kwargs)


def location_update_handler(**kwargs):
    kwargs.pop('signal', None)
    sender = kwargs.pop('sender')
    lat = kwargs.pop('lat')
    lng = kwargs.pop('lng')
    key = kwargs.pop('key', None)
    tree_type = kwargs.pop('tree')

    newlocation = LocationMgr(
        lat=lat,
        lng=lng,
        key=key,
        content_type=ContentType.objects.get_for_model(sender),
        object_id=sender.pk)

    newlocation.save()
    #update tree
    tree = LocationMgr.objects.get_tree_from_type(tree_type)
    tree[key] = sender.pk
    print 'current tree [{tree}]'.format (tree=tree)
    return newlocation

location.connect(location_update_handler, dispatch_uid='location_mgr.models.location_mgr')



