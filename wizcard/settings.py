# Django settings for wizcard project.
import os

from kombu import Queue, Exchange
from wizcard import instances

RUNENV = os.getenv('WIZRUNENV', 'dev')

APP_MAJOR = 1
APP_MINOR = 9

DEBUG = False
if RUNENV != 'prod':
    DEBUG = False
ALLOWED_HOSTS = ['*']
DEBUG_PROPAGATE_EXCEPTIONS = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

WIZCARD_SETTINGS = {
    # env: setting
    'dev': {
        'databases': {
            'default': {
                #'ENGINE': 'django.db.backends.mysql',
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'wizcard-dev',
                'USER': 'kappu',
                'PASSWORD': '',
                'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
                 'PORT': '5432',
                # 'CONN_MAX_AGE' : 60,
            }
        },
        'caches': {
            'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'default-cache'
            }
        },
        'raven_config': {
            'dsn':'https://a8d0ed041ea04ed3a5425d473c7eef4e:9334d4a08de2483f90a26402e57ddb0e@app.getsentry.com/80078',
        }
    },
    'test': {
        'databases': {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'wizcard',
                'USER': 'wizuser',
                'PASSWORD': 'gowizcard',
                'HOST': 'wizcard-prod-stage.cihg5qbd9uuc.ap-south-1.rds.amazonaws.com',
            }
        },
        'caches': {
            'default': {
                'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
                'LOCATION': instances.RUNHOSTS[RUNENV]['MEMCACHE']
            }
        },
        'raven_config': {
            'dsn':'https://a8d0ed041ea04ed3a5425d473c7eef4e:9334d4a08de2483f90a26402e57ddb0e@app.getsentry.com/80078',
        }
    },
    'stage': {
        'default': {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'wizcard-prod',
                'USER': 'wizuser',
                'PASSWORD': 'gowizcard',
                'HOST': 'wizcard-prod-clone.cihg5qbd9uuc.ap-south-1.rds.amazonaws.com',
            }
        },
        'caches': {
            'default': {
                'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
                'LOCATION': instances.RUNHOSTS[RUNENV]['MEMCACHE']
            }
        },
        'raven_config': {
            'dsn': 'https://c2ee29b3727d4d599b0fa0035c64c9fa:e7d756b3a14a4a86947c6c011e2c6122@app.getsentry.com/46407',
        }
    },
    'prod': {
        'databases': {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'wizcard-prod',
                'USER': 'wizuser',
                'PASSWORD': 'gowizcard',
                'HOST': 'wizcard-prod-live.cihg5qbd9uuc.ap-south-1.rds.amazonaws.com',
            }
        },
        'caches': {
            'default': {
                'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
                'LOCATION': instances.RUNHOSTS[RUNENV]['MEMCACHE']
            }
        },
        'raven_config': {
            'dsn': 'https://1caf9d8960e44c059330d3fea68bf1c5:5a1631aedc54436a97bd908fefa458cb@sentry.io/87350'
        }
    }
}

DATABASES = WIZCARD_SETTINGS[RUNENV]['databases']
CACHES = WIZCARD_SETTINGS[RUNENV]['caches']

# RAVEN config for Sentry
RAVEN_CONFIG = WIZCARD_SETTINGS[RUNENV]['raven_config']


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Calcutta'

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
#   'django.template.loaders.eggs.Loader',
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
PHONE_CHECK = False
if RUNENV == 'prod':
    PHONE_CHECK = True
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

#NEXMO_API_KEY = '4788a696'
#NEXMO_API_SECRET = '185e2f6f'
#NEXMO_OWN_NUMBER = '12243109118'

#This one is from wizcarder account
NEXMO_API_KEY = '46ba6fbd'
NEXMO_API_SECRET = '3c1d7f33'
NEXMO_OWN_NUMBER = '12184294228'
NEXMO_SENDERID = 'WZCARD'

EMAIL_TEMPLATE = '/invites/email_templatev4.png'
EMAIL_FROM_ADDR='wizcarder@getwizcard.com'

PHONE_CHECK_MESSAGE = {
        'reqtype': 'json',
        'api_key': NEXMO_API_KEY,
        'api_secret': NEXMO_API_SECRET,
        'from': NEXMO_SENDERID,
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
    'django_ses',
    'recommendation',
    'stats',
    'commands',
    'email_and_push_infra'
)

#django-storage settings

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = 'AKIAJ7JLJSP4BCEZ72EQ'
AWS_SECRET_ACCESS_KEY = '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'
AWS_BUCKET_ENV = "-" + RUNENV
AWS_QUERYSTRING_AUTH = False
#Expiry set to 100 years
AWS_QUERYSTRING_EXPIRE = 3153600000
AWS_STORAGE_BUCKET_NAME = 'wizcard-image-bucket' + AWS_BUCKET_ENV
S3_URL = 'http://s3.us-west-1.amazonaws.com/%s' % AWS_STORAGE_BUCKET_NAME
EMAIL_DEFAULT_IMAGE = S3_URL +  "/invites/email_info.png"
DEFAULT_VIDEO_THUMBNAIL = AWS_STORAGE_BUCKET_NAME+ "/thumbnails/no-video-uploaded.gif"

STATIC_DIRECTORY = '/static/'
MEDIA_DIRECTORY = '/media/'
STATIC_URL = S3_URL + STATIC_DIRECTORY
MEDIA_URL = S3_URL + MEDIA_DIRECTORY

#django-ses Settings
SES_SMTP_USER = 'AKIAJIXICBLUCPSKQPKA'
SES_SMTP_PASS = 'AgHl9hZWrbH51ur6WorLxNJ7ETxb8fmqHg2OUbkVDKrv'
AWS_SES_REGION_NAME = 'us-east-1'
AWS_SES_REGION_ENDPOINT = 'email.us-east-1.amazonaws.com'
EMAIL_BACKEND='django_ses.SESBackend'
AWS_RETURN_PATH='wizcarder@gmail.com'



AUTH_PROFILE_MODULE = 'wizcard.UserProfile'

# RAVEN config for Sentry
#RAVEN_CONFIG = {
#    #for new AWS prod/stage
#    'dsn': 'https://e09392c542d24e058631183b6123c1b4:159738ded89d46bba319ad5887422e9d@app.getsentry.com/41148',
#    #'CELERY_LOGLEVEL': logging.ERROR
#
#    #for bitnami AWS instance
#    #'dsn': 'https://c2ee29b3727d4d599b0fa0035c64c9fa:e7d756b3a14a4a86947c6c011e2c6122@app.getsentry.com/46407'
#}

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
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            #consider: 'filename': '/var/log/<myapp>/app.log',
            #will need perms at location below:
            'filename': './log/app.log',
            'backupCount': 5,
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
            'backupCount': '30', #approx 1 month worth
        },
        'watched-log-file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'parsefriendly',
            #consider: 'filename': '/var/log/<myapp>/app.log',
            #will need perms at location below:
            'filename': './log/app-watched.log',
            'backupCount' : 30,
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
    #  ('com.beta.wizcard', open('./certs/wizcard_ios_apns_dev.pem').read(), 'sandbox'),
    ('com.beta.wizcard', open('./certs/wizcard_ios_apns_production.pem').read(), 'production'),
  ]
}

GCM_API_KEY = 'AIzaSyAz_uc7MiPtC_JK1ZjurpsdxxDlfPAy4-c'
SHORTEN_API_KEY = 'AIzaSyBiw4HSRUb8VlR5oY0bLuRPTjT2G-fW8qo'
SHORTEN_SERVICE = 'Google'

CELERY_TIMEZONE = TIME_ZONE
SETTINGS_PATH = os.path.normpath(os.path.dirname(__file__))
# Find templates in the same folder as settings.py.
TEMPLATE_DIRS = (
            os.path.join(SETTINGS_PATH, 'templates'),
            )

# RECOMMENDATION SETTINGS
# In minutes - Interval to check for recommendation for trigger and full
FULL_RECO_GEN_INTERVAL = 5

# Default size for get_recommendations
GET_RECO_SIZE = 10

#Periodic RECO_GEN_INTERVAL
PERIODIC_RECO_GEN_INTERVAL = 1
