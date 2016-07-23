#!/usr/bin/env python
TEST_AWSHOSTS=['ec2-52-66-102-242.ap-south-1.compute.amazonaws.com']
DEV_AWSHOSTS=['ec2-54-153-11-241.us-west-1.compute.amazonaws.com']
PROD_AWSHOSTS=['ec2-54-193-120-172.us-west-1.compute.amazonaws.com','ec2-52-8-23-147.us-west-1.compute.amazonaws.com']
STG_AWSHOSTS=['localhost']

stg_memcache_hosts=[]
prod_memcache_hosts=[]
test_memcache_hosts=[]
for hosts in STG_AWSHOSTS:
    stg_memcache_hosts.append(hosts+":11211")
for hosts in PROD_AWSHOSTS:
    prod_memcache_hosts.append(hosts+":11211")
for hosts in DEV_AWSHOSTS:
    prod_memcache_hosts.append(hosts+":11211")
for hosts in TEST_AWSHOSTS:
    test_memcache_hosts.append(hosts+":11211")
ALLHOSTS = {
	'stage':{
		'LOCATIONSERVER': [STG_AWSHOSTS[0]],
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
        'test':{
            'LOCATIONSERVER':TEST_AWSHOSTS,
            'WIZSERVER':TEST_AWSHOSTS,
            'NGINX':TEST_AWSHOSTS,
            'MEMCACHE':TEST_AWSHOSTS,
        },
        'prod':{
            'LOCATIONSERVER':[PROD_AWSHOSTS[0]],
            'WIZSERVER':PROD_AWSHOSTS,
                'NGINX':PROD_AWSHOSTS,
            'MEMCACHE':prod_memcache_hosts,
        }

}

