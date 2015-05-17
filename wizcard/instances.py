#!/usr/bin/env python
STG_AWSHOSTS=['ec2-52-8-25-4.us-west-1.compute.amazonaws.com','ec2-52-8-23-147.us-west-1.compute.amazonaws.com']
PROD_AWSHOSTS=['ec2-52-8-96-234.us-west-1.compute.amazonaws.com','ec2-52-8-29-117.us-west-1.compute.amazonaws.com']

stg_memcache_hosts=[]
prod_memcache_hosts=[]
for hosts in STG_AWSHOSTS:
    stg_memcache_hosts.append(hosts+":11211")
for hosts in PROD_AWSHOSTS:
    prod_memcache_hosts.append(hosts+":11211")
ALLHOSTS = {
	'test':{
		'LOCATIONSERVER': ['ec2-52-8-25-4.us-west-1.compute.amazonaws.com'],
		'WIZSERVER':STG_AWSHOSTS,
                'NGINX':STG_AWSHOSTS,
                'MEMCACHE':stg_memcache_hosts,
	},
        'dev':{
            'LOCATIONSERVER':['localhost'],
            'WIZSERVER':['localhost'],
            'NGINX':['localhost']
        },
        'prod':{
            'LOCATIONSERVER':[PROD_AWSHOSTS[0]],
            'WIZSERVER':PROD_AWSHOSTS,
                'NGINX':PROD_AWSHOSTS,
            'MEMCACHE':prod_memcache_hosts,
        }

}

