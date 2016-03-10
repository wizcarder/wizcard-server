#!/usr/bin/env python
STG_AWSHOSTS=['ec2-52-8-141-105.us-west-1.compute.amazonaws.com','ec2-52-8-23-147.us-west-1.compute.amazonaws.com','ec2-54-183-239-37.us-west-1.compute.amazonaws.com']
PROD_AWSHOSTS=['ec2-52-8-96-234.us-west-1.compute.amazonaws.com','ec2-52-8-29-117.us-west-1.compute.amazonaws.com']
DEV_AWSHOSTS=['localhost']

stg_memcache_hosts=[]
prod_memcache_hosts=[]
for hosts in STG_AWSHOSTS:
    stg_memcache_hosts.append(hosts+":11211")
for hosts in PROD_AWSHOSTS:
    prod_memcache_hosts.append(hosts+":11211")
for hosts in DEV_AWSHOSTS:
    prod_memcache_hosts.append(hosts+":11211")
ALLHOSTS = {
	'stage':{
		'LOCATIONSERVER': [STG_AWSHOSTS[0], STG_AWSHOSTS[2]],
		'WIZSERVER':STG_AWSHOSTS,
                'NGINX':STG_AWSHOSTS,
                'MEMCACHE':stg_memcache_hosts,
	},
        'dev':{
            'LOCATIONSERVER':DEV_AWSHOSTS,
            'WIZSERVER':DEV_AWSHOSTS,
            'NGINX':DEV_AWSHOSTS,
            'MEMCACHE':DEV_AWSHOSTS,
        },
        'prod':{
            'LOCATIONSERVER':[PROD_AWSHOSTS[0]],
            'WIZSERVER':PROD_AWSHOSTS,
                'NGINX':PROD_AWSHOSTS,
            'MEMCACHE':prod_memcache_hosts,
        }

}

