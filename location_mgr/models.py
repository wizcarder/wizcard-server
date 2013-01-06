from django.db import models
from django.db import models
import datetime
from lib.pytrie import SortedStringTrie as trie
from django.contrib.auth.models import User
from lib import wizlib
import random
import pdb

class LocationMgrManager(models.Manager):
    def lookup_by_key(self, key, tree, num_results, key_in_tree=True):
        print 'looking up tree [{tree}] using key [{key}]'.format (tree=tree, key=key)
        if not tree:
            return None, None

        #AA:TODO: Kludge to dis-include self.key from the results
        if key_in_tree:
            #cache value
            val = tree[key]
            del tree[key]
        result, count =  wizlib.lookup_closest_n_values(tree, key, num_results)
        print '{count} lookup result [{result}]'.format (count=count, result=result)

        #add self back
        if key_in_tree:
            tree[key] = val
        return result, count

    def lookup_by_lat_lng(self, lat, lng, tree, num_results, key_in_tree=False):
        if not tree:
            return None, None
        key = wizlib.create_geohash(lat, lng)
        return self.lookup_by_key(key, tree, num_results, key_in_tree)

class LocationMgr(models.Model):
    lat = models.FloatField(null=True, default=None)
    lng = models.FloatField(null=True, default=None)
    key = models.CharField(null=True, max_length=100)
    lastseen = models.DateTimeField(default=datetime.datetime.now,
                                    editable=False)

    objects = LocationMgrManager()

    class Meta:
        abstract = True

    def set_location(self, lat, lng):
        changed = False
        lat = lat+random.random()
        lng = lng+random.random()
        if self.lat != lat:
            self.lat = lat
            changed = True
        if self.lng != lng:
            self.lng = lng
            changed = True
        return changed

    def update_tree(self, tree, *args, **kwargs):
        #location changed. Delete old node
        if self.key:
            try:
                del tree[self.key]
            except:
                #only reason could/should be that server was restarted
                pass
        #save new node
        if self.lat and self.lng:
            self.key = wizlib.create_geohash(self.lat, self.lng)
            tree[self.key] = self.pk
        print 'current tree [{tree}]'.format (tree=tree)
        self.save()
