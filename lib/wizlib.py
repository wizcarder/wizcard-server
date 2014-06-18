import pdb
import geohash
import gc
from django.conf import settings


#Geohash related stuff

def create_geohash(lat, lng):
    encode = geohash.encode(lat, lng)
    #print 'geohash encoded [{lat}, {lng}] to {encode}'.format (lat=lat, lng=lng, encode=encode)
    return encode

def lookup(tree, lat, lng, num_results, key=None):
    #print 'looking up tree [{tree}] using key [{key}]'.format (tree=tree, key=key)
    if not tree:
        return None, None
    if not key:
        key = create_geohash(lat, lng)
    result =  lookup_closest_n(tree, key, num_results)
    #print '{count} lookup result [{result}]'.format (count=result[1], result=result[0])
    return result[0], result[1]

def modified_key(key, val):
    mkey = settings.MKEY_SEP.join((key, str(val)))
    return mkey

def demodify_key(key):
    return key.split(settings.MKEY_SEP)[0]

def ptree_insert(key, tree, val):
    tree[key] = val

def ptree_delete(key, tree):
    val = None
    try:
	val = tree[key]
        del tree[key]
    except:
        pass
    return val

def lookup_closest_n(tree, key, n, value_only = True):
    #lookup using top half of key
    result = None
    count = 0
    left = 0
    right = len(key)
    part = right
    done = False

    while not done:
	part = ((right + left - 1)//2) + 1
        result, count = tree.longest_common_prefix_value(key[:part])
        if part == right:
            done = True

        prev_result = result
        prev_count = count

	if count < n:
	    right = part
        elif count > n:
            left = part
        else:
            break
            
    #one result is over and one is under. take the larger one

    return (result, count) if count > prev_count else (prev_result, prev_count)

#general purpose utils
def convert_phone(phone):
    import string
    remove = '() -:+'
    remove_map = dict((ord(char), None) for char in remove)
    return phone.translate(remove_map)

def queryset_iterator(queryset, chunksize=1000):
    '''
   
    Iterate over a Django Queryset ordered by the primary key 
    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.  
    Note that the implementation of the iterator does not support ordered query sets.
    '''
    if not queryset.count():
        return
    pk = 0
    last_pk = queryset.order_by('-pk')[0].pk
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()

from math import radians, cos, sin, asin, sqrt
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    m = 6367 * c * 10000
    return m
