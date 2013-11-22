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
import heapq
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
            qs = LocationMgr.objects.all()
            rows = wizlib.queryset_iterator(qs) 
            for row in rows:
                key = wizlib.create_geohash(row.lat, row.lng)
                wizlib.ptree_insert(
                        wizlib.modified_key(key, row.pk),
                        LocationMgr.objects.get_tree_from_type(row.tree_type),
                        row.pk)
                row.timer.get().start()
        except:
            return
        self.inited = True
        print 'Inited Location Trees, Inited={inited}'.format(inited=self.inited)
        self.print_trees()
	
    def get_tree_from_type(self, tree_type):
	return self.location_tree_handles[tree_type]
  
    def lookup(self, tree, lat, lng, key, n):
        result, count = wizlib.lookup(
                            lat,
                            lng,
                            key,
                            tree, 
                            n)
        #print 'looking up  gives result [{result}]'.format (result=result)
        h = []
        for l in LocationMgr.objects.filter(id__in=result):
            heapq.heappush(h, (l.distance_from(lat, lng), l.object_id))

        h_result = heapq.nsmallest(n, h)
        return [r[1] for r in h_result], count

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
        if self.lat != lat:
            self.lat = lat
            updated = True
        if self.lng != lng:
            self.lng = lng
            updated = True
        if updated:
            #delete old guy
            self.delete_from_tree()
            #add new guy
            newkey = wizlib.create_geohash(self.lat, self.lng)
            self.key = newkey
            self.save()
            #update tree with new key (and old id)
            self.insert_in_tree(),
        #print 'current tree [{tree_type}.{tree}]'.format (tree_type=self.tree_type, tree=tree)
        return updated

    def lookup(self, n):
        print 'lookup up {tree_type}'.format (tree_type=self.tree_type)
	tree = LocationMgr.objects.get_tree_from_type(self.tree_type)

	#remove self.key from the tree. Otherwise this skews the resuls towards
	#us. Even if we were to do a partwise lookup, it might still skew things
	#depending on the sparsity of the tree
	cached_val = self.delete_from_tree()
        result, count = LocationMgr.objects.lookup(tree,
                                                   self.lat,
                                                   self.lng, 
                                                   self.key, 
                                                   n)
	#add me back
	if cached_val:
	    self.insert_in_tree()

        print 'looking up  gives {count} results [{result}]'.format (count=count, result=result)
        return result, count

    def delete_from_tree(self):
        tree = LocationMgr.objects.get_tree_from_type(self.tree_type)
        val = wizlib.ptree_delete(
			wizlib.modified_key(self.key, self.pk),
			tree)
        print 'post deleted tree: [{type}.{tree}]'.format (type=self.tree_type, tree=tree)
	return val

    def insert_in_tree(self):
        tree = LocationMgr.objects.get_tree_from_type(self.tree_type)
        wizlib.ptree_insert(
                wizlib.modified_key(self.key, self.pk),
                tree,
                self.pk)
        print 'post inset tree: [{type}.{tree}]'.format (type=self.tree_type, tree=tree)

    def delete(self, *args, **kwargs):
        print 'deleting key {key}.{tree} from tree'.format (key=self.key, tree=self.tree_type)
        print 'tree before delete {tree}'.format(tree = LocationMgr.objects.get_tree_from_type(self.tree_type))
        self.delete_from_tree()
        print 'tree after delete {tree}'.format(tree = LocationMgr.objects.get_tree_from_type(self.tree_type))
        super(LocationMgr, self).delete(*args, **kwargs)

    #Database based timer implementation
    def start_timer(self, timeout):
        t = Periodic.objects.create(location=self,
                timeout_value=timeout*60)
        t.start()

    def reset_timer(self):
        if self.timer.count():
            self.timer.get().start()

    def distance_from(self, lat, lng):
        return random.random()


def location_create_handler(**kwargs):
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
    newlocation.insert_in_tree()
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

location.connect(location_create_handler, dispatch_uid='location_mgr.models.location_mgr')
location_timeout.connect(location_timeout_handler, dispatch_uid='location_mgr.models.location_mgr')
class_prepared.connect(LocationMgr.objects.init_from_db, dispatch_uid='location_mgr.models.location_mgr')
