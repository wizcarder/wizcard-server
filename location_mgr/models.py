from django.db import models
from django.db import models
import datetime
from pytrie import SortedStringTrie as trie
from django.contrib.auth.models import User
from wizserver import wizlib
import random
import pdb

class LocationMgr(models.Model):
    lat = models.FloatField(null=True, default=None)
    lng = models.FloatField(null=True, default=None)
    key = models.CharField(null=True, max_length=100)
    lastseen = models.DateTimeField(default=datetime.datetime.now,
                                    editable=False)

    def set_location(self, lat, lng):
        changed = False
        lat = lat+random.random()
        lng = lng+random.random()
        if self.lat != lat:
            #self.lat = lat
            self.lat = lat
            changed = True
        if self.lng != lng:
            self.lng = lng
            changed = True
        return changed

    def save(self, tree, *args, **kwargs):
        if self.lat and self.lng:
            self.key = wizlib.create_geohash(self.lat, self.lng)
            tree[self.key] = self.pk
        super(LocationMgr, self).save(*args, **kwargs)


    def update(self, tree, *args, **kwargs):
        #location changed. Delete old node
        if self.key:
            try:
                del tree[self.key]
            except:
                #only reason could/should be that server was restarted
                pass
        #save new node
        self.save()

    def lookup(self, tree, num_results):
        print 'looking up tree [{tree}]'.format (tree=tree)
        #AA:TODO: Kludge to dis-include self.key from the results
        del tree[self.key]
        result =  wizlib.lookup_closest_n(tree, self.key, num_results)
        print 'lookup result [{result}]'.format (result=result)

        #add self back
        tree[self.key] = self.pk
        return result


