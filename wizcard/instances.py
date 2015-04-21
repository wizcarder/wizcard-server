#!/usr/bin/env python
AWSHOSTS=['ec2-52-74-114-151.ap-southeast-1.compute.amazonaws.com','ec2-52-74-148-23.ap-southeast-1.compute.amazonaws.com']

memcache_hosts=[]
for hosts in AWSHOSTS:
    memcache_hosts.append(hosts+":11211")
ALLHOSTS = {
	'test':{
		'LOCATIONSERVER': ['ec2-52-74-114-151.ap-southeast-1.compute.amazonaws.com'],
		'WIZSERVER':AWSHOSTS,
                'NGINX':AWSHOSTS,
                'MEMCACHE':memcache_hosts,
	},
        'dev':{
            'LOCATIONSERVER':['localhost'],
            'WIZSERVER':['localhost'],
            'NGINX':['localhost']
        }

}

