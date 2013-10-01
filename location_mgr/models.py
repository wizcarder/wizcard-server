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
from django.db.models.signals import class_prepared
from lib import wizlib
from django_cron import Job
import random
import pdb

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
    __shared_state = {}

    ptree = trie()
    vtree = trie()
    wtree = trie()

    inited = False

    location_tree_handles = {
        "PTREE" : ptree,
        "WTREE" : wtree,
        "VTREE" : vtree
    }

    def __init__(self, *args, **kwargs):
        self.__dict__ = self.__shared_state
        super(LocationMgrManager, self).__init__(*args, **kwargs)

    def init_from_db(self, sender, **kwargs):
        #AA:TODO: for some reason, this class isn't showing up in the class_prepared senders
        # ideally, need to qualify this with the sender = location_mgr
        if self.inited is True:
            print 'already inited...skipping'
            return
        try:
            rows = wizlib.queryset_iterator(LocationMgr.objects.all())
        except:
            return
        for row in rows:
            key = wizlib.create_geohash(row.lat, row.lng)
            LocationMgr.objects.get_tree_from_type(row.tree_type)[key] = row.object_id
            row.timer.get().start()
        self.inited = True
        print 'Inited Location Trees, Inited={inited}'.format(inited=self.inited)
        self.print_trees()
	
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

    def print_trees(self, tree_type=None):
	if tree_type == None:
            for ttype in LocationMgr.objects.location_tree_handles:
                print '{ttype} : {tree}'.format (ttype=ttype, tree=LocationMgr.objects.location_tree_handles[ttype])
	else:
	    print '{ttype} : {tree}'.format (ttype=ttype, tree=LocationMgr.objects.location_tree_handles[ttype])
	    
class LocationMgr(models.Model):
    lat = models.FloatField(null=True, default=None)
    lng = models.FloatField(null=True, default=None)
    key = models.CharField(null=True, max_length=100)
    tree_type = models.CharField(default="PTREE", max_length=10)

    #GenericForeignKey to objects requiring locationMgr services
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    objects = LocationMgrManager()

    def __repr__(self):
        return '[' + str(self.id) + ' at ' + '(' + str(self.lat) + ', ' + str(self.lng) + ')' + ']'

    def __init__(self, *args, **kwargs):
        super(LocationMgr, self).__init__(*args, **kwargs)

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
        tree = LocationMgr.objects.get_tree_from_type(self.tree_type)
        wizlib.delete_key(
                self.key,
                tree)
        print 'current tree [{type}.{tree}]'.format (type=self.tree_type, tree=tree)

    def delete(self, *args, **kwargs):
        print 'DELETING TREE'
        print 'tree before delete {tree}'.format(tree = LocationMgr.objects.get_tree_from_type(self.tree_type))
        self.delete_key_from_tree()
        print 'tree after delete {tree}'.format(tree = LocationMgr.objects.get_tree_from_type(self.tree_type))
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
        tree_type=tree_type,
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

def location_timeout_cb(l):
    l.delete()

#AA:TODO: if this works, then it can be a generic function
def wizcard_flick_timeout_cb(l):
    l.content_object.delete()

def virtual_table_timeout_cb(l):
    l.content_object.delete()
    
def timeout_callback_execute(e):
    timeout_callback = {
        ContentType.objects.get(app_label="userprofile", model="userprofile").id    : location_timeout_cb, 
        ContentType.objects.get(app_label="wizcardship", model="wizcardflick").id   : wizcard_flick_timeout_cb, 
        ContentType.objects.get(app_label="virtual_table", model="virtualtable").id : virtual_table_timeout_cb, 
        } 
    timeout_callback[e.content_type.id](e)

location.connect(location_update_handler, dispatch_uid='location_mgr.models.location_mgr')
location_timeout.connect(location_timeout_handler, dispatch_uid='location_mgr.models.location_mgr')
class_prepared.connect(LocationMgr.objects.init_from_db, dispatch_uid='location_mgr.models.location_mgr')
