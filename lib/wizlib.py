import pdb
import geohash
import gc
from django.conf import settings


#Geohash related stuff

def create_geohash(lat, lng):
    encode = geohash.encode(lat, lng)
    print 'geohash encoded [{lat}, {lng}] to {encode}'.format (lat=lat, lng=lng, encode=encode)
    return encode

def lookup_by_key(key, tree, num_results):
    print 'looking up tree [{tree}] using key [{key}]'.format (tree=tree, key=key)
    if not tree:
        return None, None

    result, count =  lookup_closest_n_values(tree, key, num_results)
    print '{count} lookup result [{result}]'.format (count=count, result=result)
    return result, count

def modified_key(key, val):
    mkey = settings.MKEY_SEP.join((key, val))
    print 'modified key :{key}'.format(key=mkey)
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
    print 'current tree [{tree}]'.format (tree=tree)
    return val

def lookup_closest_n(tree, key, n):
    #lookup using top half of key
    res_array = []
    count = 0
    left = 0
    right = len(key)
    part = right
    result, count = tree.longest_common_prefix_item(key[:part])
    if count > n:
        return (result, count)

    while right - left > 1:
	part = (right + left)//2
        result, count = tree.longest_common_prefix_item(key[:part])
	if count < n:
	    right = part 
	else:
            left = part
	res_array.append((result, count))

    

def lookup_closest_n_values(tree, key, n):
    return tree.longest_common_prefix_value(key)

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
