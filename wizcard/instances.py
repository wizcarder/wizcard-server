#!/usr/bin/env python
TEST_AWSHOSTS = ['ec2-35-154-226-141.ap-south-1.compute.amazonaws.com']
DEV_AWSHOSTS = ['localhost']
#PROD_AWSHOSTS = ['ec2-35-154-15-196.ap-south-1.compute.amazonaws.com',
#		'ec2-35-154-4-181.ap-south-1.compute.amazonaws.com']
PROD_AWSHOSTS = ['ec2-35-154-61-96.ap-south-1.compute.amazonaws.com',
		'ec2-35-154-91-109.ap-south-1.compute.amazonaws.com']
STG_AWSHOSTS = ['ec2-35-154-81-185.ap-south-1.compute.amazonaws.com']
LOCALHOST = ['localhost']

ALLHOSTS = {
    'stage': {
        'RABBITSERVER': LOCALHOST,
        'RECOSERVER': STG_AWSHOSTS,
        'LOCATIONSERVER':STG_AWSHOSTS,
        'WIZSERVER': STG_AWSHOSTS,
        'NGINX': STG_AWSHOSTS,
        'MEMCACHE': STG_AWSHOSTS,
    },
    'dev': {
        'RABBITSERVER': LOCALHOST,
	'LOCATIONSERVER':DEV_AWSHOSTS,
        'RECOSERVER': DEV_AWSHOSTS,
        'WIZSERVER': DEV_AWSHOSTS,
        'NGINX': DEV_AWSHOSTS,
        'MEMCACHE': DEV_AWSHOSTS,
    },
    'test': {
        'RABBITSERVER': LOCALHOST,
	'RECOSERVER' : TEST_AWSHOSTS,
        'LOCATIONSERVER': TEST_AWSHOSTS,
        'WIZSERVER': TEST_AWSHOSTS,
        'NGINX': TEST_AWSHOSTS,
        'MEMCACHE': TEST_AWSHOSTS,
    },
    'prod': {
        'RABBITSERVER': LOCALHOST,
        'LOCATIONSERVER': [PROD_AWSHOSTS[0]],
        'WIZSERVER': PROD_AWSHOSTS,
        'NGINX': PROD_AWSHOSTS,
        'MEMCACHE': PROD_AWSHOSTS,
    }
}

RUNHOSTS = {'dev': {'LOCATIONSERVER': ['localhost'],
         'MEMCACHE': ['localhost:11211'],
         'NGINX': ['localhost'],
         'RABBITSERVER': ['localhost'],
         'RECOSERVER': ['localhost'],
         'WIZSERVER': ['localhost']},
 'prod': {'LOCATIONSERVER': ['172.31.20.255'],
          'MEMCACHE': ['172.31.20.255:11211',
                       '172.31.20.254:11211'],
          'NGINX': ['172.31.20.255',
                    '172.31.20.254'],
          'RABBITSERVER': ['localhost'],
          'WIZSERVER': ['172.31.20.255',
                        '172.31.20.254']},
 'stage': {'LOCATIONSERVER': ['172.31.9.38'],
           'MEMCACHE': ['172.31.9.38:11211'],
           'NGINX': ['172.31.9.38'],
           'RABBITSERVER': ['localhost'],
           'RECOSERVER': ['172.31.9.38'],
           'WIZSERVER': ['172.31.9.38']},
 'test': {'LOCATIONSERVER': ['172.31.2.49'],
          'MEMCACHE': ['172.31.2.49:11211'],
          'NGINX': ['172.31.2.49'],
          'RABBITSERVER': ['localhost'],
          'RECOSERVER': ['172.31.2.49'],
          'WIZSERVER': ['172.31.2.49']}}
