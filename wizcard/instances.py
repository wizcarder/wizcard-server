from __future__ import absolute_import
# ^^^ The above is required if you want to import from the celery
# library. If you don't have this then `from celery.schedules import
# becomes `proj.celery.schedules` in Python 2.x since it allows
# for relative imports by default.
# Celery settings


ALLHOSTS = {
	'test':{
		'LOCATIONSERVER': ['ec2-52-74-128-1.ap-southeast-1.compute.amazonaws.com'],
		'WIZSERVER':['ec2-52-74-128-1.ap-southeast-1.compute.amazonaws.com','ec2-52-74-60-152.ap-southeast-1.compute.amazonaws.com'],
	},
        'dev':{
            'LOCATIONSERVER':['localhost'],
            'WIZSERVER':['localhost'],
        }
}
