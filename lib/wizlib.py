import pdb
import geohash
import gc


#Geohash related stuff

def create_geohash(lat, lng):
    encode = geohash.encode(lat, lng)
    print 'geohash encoded [{lat}, {lng}] to {encode}'.format (lat=lat, lng=lng, encode=encode)
    return encode

def lookup_by_key(key, tree, num_results, key_in_tree=True):
    print 'looking up tree [{tree}] using key [{key}]'.format (tree=tree, key=key)
    if not tree:
        return None, None

    #AA:TODO: Kludge to dis-include self.key from the results
    if key_in_tree:
        #cache value
        try:
            val = tree[key]
            del tree[key]
        #on restart, it may not be there...pass
        except:
            val = None

    result, count =  lookup_closest_n_values(tree, key, num_results)
    print '{count} lookup result [{result}]'.format (count=count, result=result)

    #add self back
    if key_in_tree and val:
        tree[key] = val

    return result, count

def delete_key(key, tree):
    try:
        del tree[key]
    except:
        pass
    print 'current tree [{tree}]'.format (tree=tree)


def lookup_closest_n(tree, key, n):
    return tree.longest_common_prefix_item(key)

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
     pk = 0
     last_pk = queryset.order_by('-pk')[0].pk
     queryset = queryset.order_by('pk')
     while pk < last_pk:
         for row in queryset.filter(pk__gt=pk)[:chunksize]:
             pk = row.pk
             yield row
         gc.collect()
