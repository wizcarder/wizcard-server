from django.db import models
import datetime
from lib.pytrie import SortedStringTrie as trie
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from location_mgr.signals import location, location_timeout
from notifications.models import notify, Notification
from django.db.models.signals import pre_delete
from periodic.models import Periodic
from lib import wizlib
from django_cron import Job
import random
import pdb

ptree = trie()
wtree = trie()
vtree = trie()

class Tick(Job):
    run_every = 10

    def job(self):
        print 'TICK RECEIVED'
        e = Periodic.objects.get_expired()
        if e.count():
            print 'EXPIRED objects found {e}'.format(e=e)
            ids = map(lambda x:  x.location.pk, e)
            location_timeout.send(sender=None, ids=ids)


class LocationMgrManager(models.Manager):

    PTREE = 1 
    WTREE = 2
    VTREE = 3

    location_tree_handles = {
        PTREE : ptree,
        WTREE : wtree,
        VTREE : vtree
    }

    def get_tree_from_type(self, tree_type):
	return self.location_tree_handles[tree_type]
  
    def lookup_by_key(self, tree_type, key, n, key_in_tree=True):
	tree = self.get_tree_from_type(tree_type)
        #print 'current tree [{tree_type}.{tree}]'.format (tree_type=tree_type, tree=tree)
        result, count = wizlib.lookup_by_key(key, 
                                             tree, 
                                             n,
                                             key_in_tree)
        #print 'looking up  gives result [{result}]'.format (result=result)
        return result, count

    def lookup_by_lat_lng(self, tree_type, lat, lng, n):
        key = wizlib.create_geohash(lat, lng)
        return self.lookup_by_key(tree_type, key, n, False)

class LocationMgr(models.Model):
    lat = models.FloatField(null=True, default=None)
    lng = models.FloatField(null=True, default=None)
    key = models.CharField(null=True, max_length=100)
    tree_type = models.IntegerField(default=LocationMgrManager.PTREE)

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
        
        #print 'current tree [{tree_type}.{tree}]'.format (tree_type=self.tree_type, tree=tree)
        return updated

    def delete_key_from_tree(self):
        wizlib.delete_key(
                self.key,
                LocationMgr.objects.get_tree_from_type(self.tree_type))
        print 'current tree [{type}.{tree}]'.format (type=self.tree_type, tree=LocationMgr.objects.get_tree_from_type(self.tree_type))

    def delete(self, *args, **kwargs):
        print 'DELETING TREE'
        print 'tree before delete {tree}'.format(tree = LocationMgr.objects.get_tree_from_type(self.tree_type))
        self.delete_key_from_tree()
        print 'tree after delete {type}.{tree}'.format(type=self.tree_type, tree=LocationMgr.objects.get_tree_from_type(self.tree_type))
        super(LocationMgr, self).delete(*args, **kwargs)

    #Database based timer implementation
    def start_timer(self, timeout):
        t = Periodic.objects.create(location=self,
                timeout_value=timeout*60)
        t.start()

    def reset_timer(self):
        if self.timer.count():
            self.timer.all()[0].start()

def location_update_handler(**kwargs):
    kwargs.pop('signal', None)
    sender = kwargs.pop('sender')
    lat = kwargs.pop('lat')
    lng = kwargs.pop('lng')
    key = kwargs.pop('key', None)
    tree_type = kwargs.pop('tree', None)

    newlocation = LocationMgr(
        lat=lat,
        lng=lng,
        key=key,
        tree_type = tree_type,
        content_type=ContentType.objects.get_for_model(sender),
        object_id=sender.pk)

    newlocation.save()
    #update tree
    tree = LocationMgr.objects.get_tree_from_type(newlocation.tree_type)
    tree[key] = sender.pk
    #print 'current tree [{tree}]'.format (tree=tree)
    return newlocation

def location_timeout_handler(**kwargs):
    ids = kwargs.pop('ids')
    expired = map(lambda x: LocationMgr.objects.get(id=x), ids)
    for e in expired:
        timeout_callback_execute(e)

def user_location_timeout_cb(l):
    l.delete()

def wizcard_flick_timeout_cb(l):
    l.content_object.delete()
    l.delete()

def virtual_table_timeout_cb(l):
    l.content_object.delete()
    l.delete()
    
def timeout_callback_execute(e):
    timeout_callback = {
        ContentType.objects.get(app_label="userprofile", model="userprofile").id    : user_location_timeout_cb, 
        ContentType.objects.get(app_label="wizcardship", model="wizcardflick").id   : wizcard_flick_timeout_cb, 
        ContentType.objects.get(app_label="virtual_table", model="virtualtable").id : virtual_table_timeout_cb, 
        } 
    timeout_callback[e.content_type.id](e)

location.connect(location_update_handler, dispatch_uid='location_mgr.models.location_mgr')
location_timeout.connect(location_timeout_handler, dispatch_uid='location_mgr.models.location_mgr')
