import pdb
import geohash
import gc
from django.conf import settings


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

#Geohash related stuff

def create_geohash(lat, lng):
    encode = geohash.encode(lat, lng)
    #print 'geohash encoded [{lat}, {lng}] to {encode}'.format (lat=lat, lng=lng, encode=encode)
    return encode

def modified_key(key, val):
    mkey = settings.MKEY_SEP.join((key, str(val)))
    return mkey

def demodify_key(key):
    return key.split(settings.MKEY_SEP)[0]

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

#reverse geocoding
from pygeocoder import Geocoder
def reverse_geo_from_latlng(lat, lng):
    result = Geocoder.reverse_geocode(lat, lng)

    #route, city
    #city, country
    #bailA

    #should expand this to include known locations, buildings etc
    route = result.route
    city = result.city
    country = result.country
   
    out = ""
    if route:
        out = route + ", " + city
    elif city:
        out = city + ", " + country
    else:
        out = country

    return out

def format_location_name(location):
    return "@"+location if location else "@location unknown"


# phone number cleanup
def clean_phone_number(phone, international_prefix, country_code):
    return phone
