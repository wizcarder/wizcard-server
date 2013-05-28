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

    def get_tree_from_type(self):
	return self.location_tree_handles[self.tree_type]
  
    def get_tree_from_content_type(self, type):
	#AA_TODO
	return PTREE

    def lookup_by_key(self, key, n, key_in_tree=True):
	tree = self.get_tree_from_type(self.tree_type)
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

    def default_callback_fn(self, id):
        LocationMgr.objects.get(id=id).delete_key_from_tree()
        
class LocationMgr(models.Model):
    lat = models.FloatField(null=True, default=None)
    lng = models.FloatField(null=True, default=None)
    key = models.CharField(null=True, max_length=100)
    tree_type = models.IntegerField(default=LocationMgr.objects.PTREE)
    timer_id = models.PositiveIntegerField(null=True)

    #GenericForeignKey to objects requiring locationMgr services
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    objects = LocationMgrManager()

    def do_update(self, lat, lng):
	tree = LocationMgr.objects.get_tree_from_type(self.tree_type)
        updated = False
        object_id = self.object_id
        if self.lat != lat:
            self.lat = lat
            updated = True
        if self.lng != lng:
            self.lng = lng
            updated = True
        if updated:
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
        elif not tree.has_key(self.key):
            tree[self.key] = object_id
        
        print 'current tree [{tree}]'.format (tree=tree)
        return updated

    def delete_key_from_tree(self):
        wizlib.delete_key(
                LocationMgr.objects.get_tree_from_type(self.tree_type),
                self.key)

    def delete(self, *args, **kwargs):
        #AA_TODO: move above function here once treey_type usage 
        #is not  required
        super(VirtualTable, self).delete(*args, **kwargs)

    def start_timer(self, *args, **kwargs):
        callback_fn = kwargs.pop('callback_fn', default_callback_fn)
        timeout = kwargs.pop('timeout')
        t = timer.Timer(timeout=timeout, callback_fn=callback_fn, kwargs)
	self.timer_id = t.start()

    def stop_timer(self):
        timer.Timer.id2obj(self.timer_id).stop()

    def reset_timer(self):
        timer.Timer.id2obj(self.timer_id).reset()

    def destroy_timer(self):
        timer.Timer.id2obj(self.timer_id).destroy()
        self.timer_id = None

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



