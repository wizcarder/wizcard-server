#####celery related stuff######
from __future__ import absolute_import
# ^^^ The above is required if you want to import from the celery
# library. If you don't have this then `from celery.schedules import
# becomes `proj.celery.schedules` in Python 2.x since it allows
# for relative imports by default.
# Celery settings
import djcelery
import os
djcelery.setup_loader()
import logging

from kombu import Queue, Exchange
from wizcard import instances

TEST = False
RUNENV = os.getenv('WIZRUNENV','dev')
BROKER_TRANSPORT = 'amqp'
BROKER_USER = 'wizcard_user'
LOCATION_USER = 'location_user'
LOCATION_PASS = 'location_pass'
BROKER_PASSWORD = 'wizcard_pass'
BROKER_HOST = 'localhost'
BROKER_PORT = 5672
BROKER_VHOST = 'wizcard_vhost'

#CELERY_RESULT_BACKEND = 'amqp://'
CELERY_RESULT_BACKEND = 'rpc'

IMAGE_UPLOAD_QUEUE_NAME = 'image_upload'
EMAIL_TEMPLATE = '/invites/email_templatev3.png'
OCR_QUEUE_NAME = 'ocr'
CELERY_DEFAULT_QUEUE = 'default'
CELERY_BEAT_QUEUE_NAME = 'beat'

CELERY_IMAGE_UPLOAD_Q = Queue(IMAGE_UPLOAD_QUEUE_NAME,
                              Exchange(IMAGE_UPLOAD_QUEUE_NAME),
                              routing_key=IMAGE_UPLOAD_QUEUE_NAME)

CELERY_OCR_Q = Queue(OCR_QUEUE_NAME,
                     Exchange(OCR_QUEUE_NAME),
                     routing_key=OCR_QUEUE_NAME)

CELERY_DEFAULT_Q = Queue(CELERY_DEFAULT_QUEUE,
                         Exchange(CELERY_DEFAULT_QUEUE),
                         routing_key=CELERY_DEFAULT_QUEUE,
                         delivery_mode=1)

CELERY_BEAT_Q = Queue(CELERY_BEAT_QUEUE_NAME,
                         Exchange(CELERY_BEAT_QUEUE_NAME),
                         routing_key=CELERY_BEAT_QUEUE_NAME,
                         delivery_mode=1)

CELERY_QUEUES = (
            CELERY_IMAGE_UPLOAD_Q,
            CELERY_OCR_Q,
            CELERY_DEFAULT_Q,
            CELERY_BEAT_Q
)

CELERY_ROUTES = {
    'queued_storage.tasks.Transfer': {
        'queue': IMAGE_UPLOAD_QUEUE_NAME,
        'routing_key': IMAGE_UPLOAD_QUEUE_NAME
    }
}

from datetime import timedelta
CELERYBEAT_SCHEDULE = {
    'tick': {
        'task': 'periodic.tasks.tick',
        'schedule': timedelta(seconds=60),
        'options': {'queue': CELERY_BEAT_QUEUE_NAME}
    },
}


# Django settings for wizcard project.

DEBUG = False
ALLOWED_HOSTS = ['*']
DEBUG_PROPAGATE_EXCEPTIONS = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

if RUNENV == 'dev' or RUNENV=='test':
    DATABASES = {
	    'default': {
	        'ENGINE': 'django.db.backends.postgresql_psycopg2',
	        'NAME': 'wizcard',
	        'USER': 'wizuser',
	        'PASSWORD': 'gowizcard',
                'HOST': 'wizcardpostgres.caqhxrq8dyl5.us-west-1.rds.amazonaws.com', # Set to empty string for localhost. Not used with sqlite3.
                'PORT': '5432',
	    }
#    DATABASES = {
#	    'default': {
#	        'ENGINE': 'django.db.backends.mysql',
#	        'NAME': 'wizcard',
#	        'USER': 'root',
#	        'PASSWORD': 'mydb',
#                'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
#	    }

    }
elif RUNENV == 'stage':
    DATABASES = {
	    'default': {
	        'ENGINE': 'django.db.backends.postgresql_psycopg2',
	        'NAME': 'wizcard-prod',
	        'USER': 'wizuser',
	        'PASSWORD': 'gowizcard',
                'HOST': 'wizcardpostgres.caqhxrq8dyl5.us-west-1.rds.amazonaws.com', # Set to empty string for localhost. Not used with sqlite3.
	    }
    }
elif RUNENV == 'prod':
    DATABASES = {
	    'default': {
	        'ENGINE': 'django.db.backends.mysql',
	        'NAME': 'wizcard',
	        'USER': 'wizuser',
	        'PASSWORD': 'wizcarddb',
            'HOST': 'wizcardprod.caqhxrq8dyl5.us-west-1.rds.amazonaws.com', # Set to empty string for localhost. Not used with sqlite3.
	    }
    }

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '/tmp/media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'lj*=)*k$_^rx3bs+22=*og)d=eh)(jdc4df!q5=b!%&amp;0kskuad'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'pagination.middleware.PaginationMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# Setup caching per Django docs. In actuality, you'd probably use memcached instead of local memory.
if RUNENV == 'dev':
    CACHES = {
     'default': {
         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
         'LOCATION': 'default-cache'
     }
    }
elif RUNENV == 'stage':
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': instances.ALLHOSTS[RUNENV]['MEMCACHE']
        }
    }
elif RUNENV == 'prod':
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': instances.ALLHOSTS[RUNENV]['MEMCACHE']
        }
    }




DEFAULT_MAX_LOOKUP_RESULTS = 20
DEFAULT_MAX_MEISHI_LOOKUP_RESULTS = 2

# Number of seconds of inactivity before a user is marked offline
USER_ONLINE_TIMEOUT = 10    #seconds
USER_ACTIVE_TIMEOUT = 1     #minutes
USER_ONLINE_PREFIX = 'seen_%s'

#radius for agglomerating flicked cards (in meters)
DO_FLICK_AGGLOMERATE = True
WIZCARD_FLICK_AGGLOMERATE_RADIUS = 1000
WIZCARD_FLICK_DEFAULT_TIMEOUT = 1

#default table lifetime
WIZCARD_DEFAULT_TABLE_LIFETIME = 5

# Number of seconds that we will keep track of inactive users for before
# their last seen is removed from the cache
USER_LASTSEEN_TIMEOUT = 60

#max number of phone check attempt per code
MAX_PHONE_CHECK_RETRIES = 3

#for UT..avoid nexmo
PHONE_CHECK =  True
#retry timeout
PHONE_CHECK_TIMEOUT = 180

PHONE_CHECK_RAND_LOW = 1000
PHONE_CHECK_RAND_HI = 9999
PHONE_CHECK_REQ_PREFIX = 'phone_check_req'
PHONE_CHECK_USER = '__user_%s'
PHONE_CHECK_RAND = '__rand_%s'
PHONE_CHECK_RETRY = '__retries_%s'
PHONE_CHECK_DEVICE_ID = '__device_id_%s'
PHONE_CHECK_USER_KEY = PHONE_CHECK_REQ_PREFIX + PHONE_CHECK_USER
PHONE_CHECK_USER_RAND_KEY = PHONE_CHECK_REQ_PREFIX + PHONE_CHECK_RAND
PHONE_CHECK_USER_RETRY_KEY = PHONE_CHECK_REQ_PREFIX + PHONE_CHECK_RETRY
PHONE_CHECK_DEVICE_ID_KEY = PHONE_CHECK_REQ_PREFIX + PHONE_CHECK_DEVICE_ID

PHONE_CHECK_RESPONSE_SMS_GREETING = "please use the following key to sign up: %s"
PHONE_CHECK_RESPONSE_VOICE_GREETING = "please use the following key to sign up: %s"
PHONE_CHECK_RESPONSE_FROM_ID = 12134657949

WIZCARD_USERNAME_EXTENSION = '@wizcard.com'
WIZCARD_FUTURE_USERNAME_EXTENSION = '@future.com'

WIZWEB_DEVICE_ID = 'wizweb'

NEXMO_API_KEY = '4788a696'
NEXMO_API_SECRET = '185e2f6f'
NEXMO_OWN_NUMBER = '12243109118'

#This one is from wizcarder account
#NEXMO_API_KEY = '46ba6fbd'
#NEXMO_API_SECRET = '3c1d7f33'
#NEXMO_OWN_NUMBER = '12184294228'

PHONE_CHECK_MESSAGE = {
        'reqtype': 'json',
        'api_key': NEXMO_API_KEY,
        'api_secret': NEXMO_API_SECRET,
        'from':NEXMO_OWN_NUMBER,
        'to':None,
        'text':""
    }


#number of per user notifs we want to process per get
NOTIF_BATCH_SIZE = 10
#seperator for modified key
MKEY_SEP = '.'

ROOT_URLCONF = 'wizcard.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wizcard.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    'django.utils.timezone',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'django_extensions',
    'djcelery',
    'storages',
    'userprofile',
    'wizserver',
    'wizcardship',
    'notifications',
    'virtual_table',
    'location_mgr',
    'dead_cards',
    'periodic',
    'gunicorn',
    'raven.contrib.django.raven_compat',
    'meishi',
    'healthstatus',
)

#django-storage settings
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = 'AKIAJ7JLJSP4BCEZ72EQ'
AWS_SECRET_ACCESS_KEY = '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'
AWS_BUCKET_ENV = "-" + RUNENV
AWS_STORAGE_BUCKET_NAME = 'wizcard-image-bucket' + AWS_BUCKET_ENV
S3_URL = 'http://s3.us-west-1.amazonaws.com/%s' % AWS_STORAGE_BUCKET_NAME
STATIC_DIRECTORY = '/static/'
MEDIA_DIRECTORY = '/media/'
STATIC_URL = S3_URL + STATIC_DIRECTORY
MEDIA_URL = S3_URL + MEDIA_DIRECTORY



AUTH_PROFILE_MODULE = 'wizcard.UserProfile'

# RAVEN config for Sentry
RAVEN_CONFIG = {
    #for new AWS prod/stage
    'dsn': 'https://e09392c542d24e058631183b6123c1b4:159738ded89d46bba319ad5887422e9d@app.getsentry.com/41148',
    'CELERY_LOGLEVEL': logging.ERROR

    #for bitnami AWS instance
    #'dsn': 'https://c2ee29b3727d4d599b0fa0035c64c9fa:e7d756b3a14a4a86947c6c011e2c6122@app.getsentry.com/46407'
}

# Advanced Django 1.3.x+ Logging
#
# Author:
# Jason Giedymin < jasong _[_a-t_]_ apache d-o-t org >
#
# Description:
# A Django 1.3.x+ settings.py snippet with Advanced logging formatters using RFC 2822,
# TimedRotatingFileHandler, and a WatchedFileHandler.
#
# NOTES: Levels are set to DEBUG! Change them or programmatically do switching (if x: LOGGING=LOGGING_DEV).
# The TimedRotatingFileHandler won't rotate unless your app is restarted.
# Use WatchedFileHandler instead, and rotate logs with a cron job or with some other program.
#
#... somewhere in settings.py or imported ...

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
            'datefmt': '%a, %d %b %Y %H:%M:%S %z',
            },
        'simple': {
            'format': '[%(levelname)s] %(asctime)s - %(message)s',
            'datefmt': '%a, %d %b %Y %H:%M:%S %z',
        },
        'django-default-verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'common-logging-v2': {
            'format': '[%(asctime)s] - %(message)s',
            'datefmt': '%d/%b/%Y:%H:%M:%S %z',
        },
        'parsefriendly': {
            'format': '[%(levelname)s] %(asctime)s - M:%(module)s, P:%(process)d, T:%(thread)d, MSG:%(message)s',
            'datefmt': '%d/%b/%Y:%H:%M:%S %z',
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console-simple':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'log-file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'verbose',
            #consider: 'filename': '/var/log/<myapp>/app.log',
            #will need perms at location below:
                'filename': './log/app.log',
            'mode': 'a', #append+create
        },
        'timed-log-file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler', # Python logging lib
            'formatter': 'parsefriendly',
            #consider: 'filename': '/var/log/<myapp>/app.log',
            #will need perms at location below:
            'filename': './log/app-timed.log',
            'when': 'midnight',
            #'backupCount': '30', #approx 1 month worth
        },
        'watched-log-file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'parsefriendly',
            #consider: 'filename': '/var/log/<myapp>/app.log',
            #will need perms at location below:
            'filename': './log/app-watched.log',
            'mode': 'a', #append+create
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
    },
    'loggers': {
	    'django': {
	        'level':'DEBUG',
	        'handlers': ['timed-log-file'],
	        'propagate': False,
	    },
        #AA TODO: Need to figure this out. Sentry logging still not working
        'raven': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'wizserver': {
            'level': 'DEBUG',
	        'handlers': ['console', 'watched-log-file'],
            'propagate': False,
        },

    }
}

APP_ID = 'com.beta.wizcard'
PYAPNS_CONFIG = {
  'HOST': 'http://localhost:7077/',
  'TIMEOUT': 1,                    # OPTIONAL, host timeout in seconds
  'INITIAL': [                      # OPTIONAL, see below
    #('com.beta.wizcard', open('./certs/wizcard_ios_apns_dev.pem').read(), 'sandbox'),
    ('com.beta.wizcard', open('./certs/wizcard_ios_apns_production.pem').read(), 'production'),
  ]
}

if RUNENV == "stage":
# RAVEN config for Sentry
    RAVEN_CONFIG = {
    #for new AWS prod/stage
        'dsn': 'https://e09392c542d24e058631183b6123c1b4:159738ded89d46bba319ad5887422e9d@app.getsentry.com/41148',
    }
elif RUNENV == "test" or RUNENV == "dev":
    RAVEN_CONFIG = {
        'dsn': 'https://c2ee29b3727d4d599b0fa0035c64c9fa:e7d756b3a14a4a86947c6c011e2c6122@app.getsentry.com/46407'
    }
GCM_API_KEY = 'AIzaSyDimK6uqvYF_GckgNpP5xf2Fofqw7pM0eE'

CELERY_TIMEZONE = 'UTC'

