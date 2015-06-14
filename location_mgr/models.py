from django.db import models
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
from django_cron.models import Cron
from django.utils import timezone
from wizserver import verbs
from location_service.client import LocationServiceClient
import logging
import heapq
import random
import time
import pdb

logger = logging.getLogger(__name__)
class Tick(Job):
    run_every = 10

    def job(self):
        logger.debug('TICK RECEIVED at %s', timezone.now())

        if os.getenv('WIZRUNENV','dev') == 'dev':
            print 'TICK RECEIVED at {t}'.format(t=timezone.now())
        exp = Periodic.objects.get_expired()
        if exp.count():
            logger.info('EXPIRED objects found %s', exp)
            ids = map(lambda x:  x.location.pk, exp)
            try:
                location_timeout.send(sender=None, ids=ids)
            except Exception, e:
		#most likely something happened when notifs were processed
		#I have seen it happen when nexmo send fails
                logger.error('Timer Job Exception: %s', str(e))
                pass

class LocationMgrManager(models.Manager):
    def init_from_db(self, sender, **kwargs):
        #just to be safe, restore django.cron executing to false
        try:
            c = Cron.objects.get(id=1)
            c.executing = False
            c.save()
        except:
            #will happen on db full clean
            pass

    def lookup(self, cache_key, tree_type, lat, lng, n,
               exclude_self=False, modifier=None):
        tsc = LocationServiceClient()

        key = wizlib.create_geohash(lat, lng)
        if exclude_self and modifier:
            key = wizlib.modified_key(key, modifier)

        result, count = tsc.lookup(tree_type=tree_type,
			           key=key,
                                   n=n,
                                   exclude_self=exclude_self)

        if not count:
            return result, count

        logger.debug('looking up  gives {%d} result {%s}', count, result)
        print('looking up  gives {} result {}'.format(count, result))

        h = []
        for l in LocationMgr.objects.filter(id__in=result):
            heapq.heappush(h, (l.distance_from(lat, lng), l.object_id))

        h_result = heapq.nsmallest(n, h)
        return [r[1] for r in h_result], count

class LocationMgr(models.Model):
    lat = models.DecimalField(null=True, max_digits=20, 
                              decimal_places=15, default=None)
    lng = models.DecimalField(null=True, max_digits=20, 
                              decimal_places=15, default=None)
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

    def is_eq_lat_lng(self, lat, lng):
        return bool( (float(self.lat) == lat and float(self.lng) == lng))

    def do_update(self, lat, lng):
        updated = False
        if not self.is_eq_lat_lng(lat, lng):
            #delete old guy
            self.delete_from_tree()
            #update self
            self.lat = lat
            self.lng = lng
            self.key = wizlib.create_geohash(self.lat, self.lng)
            self.save()
            #add new guy
            self.insert_in_tree()
            updated = True

        return updated

    def delete_from_tree(self):
        tsc = LocationServiceClient()
        val = tsc.tree_delete(
			key=wizlib.modified_key(self.key, self.pk),
			tree_type=self.tree_type)
        logger.debug('deleted from tree: [{%s}.{%s}]', self.tree_type, self.key)
	return val

    def insert_in_tree(self):
        tsc = LocationServiceClient()
        tsc.tree_insert(
                key=wizlib.modified_key(self.key, self.pk),
                tree_type=self.tree_type,
                val=self.pk)

        logger.debug('inserted into tree: [{%s}.{%s}]', self.tree_type, self.key)

    def delete(self, *args, **kwargs):
        self.delete_from_tree()
        super(LocationMgr, self).delete(*args, **kwargs)

    def lookup(self, cache_key, n):
        return LocationMgr.objects.lookup(
                cache_key,
                self.tree_type,
                self.lat,
                self.lng,
                n,
                exclude_self=True,
                modifier=self.pk)

    #Database based timer implementation
    def start_timer(self, timeout):
        t = Periodic.objects.create(location=self,
                timeout_value=timeout*60)
        return t.start()

    def extend_timer(self, timeout):
	#timeout is the timeout delta to extend by in mins
        return self.timer.get().extend_timer(timeout*60)

    def reset_timer(self, timeout=None):
        if self.timer.count():
            return self.timer.get().restart(timeout)
        return None

    def distance_from(self, lat, lng):
        return wizlib.haversine(self.lng, self.lat, lng, lat)


def location_create_handler(**kwargs):
    kwargs.pop('signal', None)
    sender = kwargs.pop('sender')
    lat = kwargs.pop('lat')
    lng = kwargs.pop('lng')
    tree_type = kwargs.pop('tree', None)

    key = wizlib.create_geohash(lat, lng)
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
    logger.debug("inserted key %s in tree %s", key, tree_type)
    return newlocation

def location_timeout_handler(**kwargs):
    ids = kwargs.pop('ids')
    expired = map(lambda x: LocationMgr.objects.get(id=x), ids)
    for e in expired:
	timeout_callback_execute(e)

def location_timeout_cb(l):
    l.delete()

def virtual_table_timeout_cb(l):
    l.content_object.delete(type=verbs.WIZCARD_TABLE_TIMEOUT[0])
    
def flicked_card_timeout(l):
    l.content_object.delete(type=verbs.WIZCARD_FLICK_TIMEOUT[0])

def timeout_callback_execute(e):
    timeout_callback = {
        ContentType.objects.get(app_label="userprofile", model="userprofile").id    : location_timeout_cb,
        ContentType.objects.get(app_label="wizcardship", model="wizcardflick").id   : flicked_card_timeout,
        ContentType.objects.get(app_label="virtual_table", model="virtualtable").id : virtual_table_timeout_cb,
        }
    timeout_callback[e.content_type.id](e)

location.connect(location_create_handler, dispatch_uid='location_mgr.models.location_mgr')
location_timeout.connect(location_timeout_handler, dispatch_uid='location_mgr.models.location_mgr')
class_prepared.connect(LocationMgr.objects.init_from_db, dispatch_uid='location_mgr.models.location_mgr')
