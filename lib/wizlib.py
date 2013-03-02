import pdb
import geohash


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
        val = tree[key]
        del tree[key]

    result, count =  lookup_closest_n_values(tree, key, num_results)
    print '{count} lookup result [{result}]'.format (count=count, result=result)

    #add self back
    if key_in_tree:
        tree[key] = val

    return result, count

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
