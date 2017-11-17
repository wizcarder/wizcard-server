# Django settings for wizcard project.
import os

from kombu import Queue, Exchange
from wizcard import instances

RUNENV = os.getenv('WIZRUNENV', 'dev')

APP_MAJOR = 1
APP_MINOR = 0

DEBUG = False
if RUNENV != 'prod':
    DEBUG = False
ALLOWED_HOSTS = ['*']
DEBUG_PROPAGATE_EXCEPTIONS = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Wizard of WizCard', 'wizcarder@getwizcard.com'),
)

MANAGERS = ADMINS

WIZCARD_SETTINGS = {
    # env: setting
    'dev': {
        'databases': {
            'default': {
                #'ENGINE': 'django.db.backends.mysql',
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'girnar-dev',
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
    },
    'test': {
        'databases': {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'girnar-stage',
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
    },
    'stage': {
        'databases': {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'girnar-live',
                'USER': 'girnar_user',
                'PASSWORD': 'neminath',
                'HOST': 'girnar-live.cvfcdhihy65l.ap-south-1.rds.amazonaws.com',
            }
        },
        'caches': {
            'default': {
                'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
                'LOCATION': instances.RUNHOSTS[RUNENV]['MEMCACHE']
            }
        }
    },
    'prod': {
        'databases': {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'girnar-live',
                'USER': 'girnar_user',
                'PASSWORD': 'neminath',
                'HOST': 'girnar-live.cvfcdhihy65l.ap-south-1.rds.amazonaws.com',
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
if RUNENV == 'prod':
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


MAX_NAME_LEN = 30

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

DISABLE_LOCATION = True
EVENT_DISABLE_USERS = True


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
EMAIL_FROM_ADDR='WizCard Inc <wizcarder@getwizcard.com>'

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

SETTINGS_PATH = os.path.normpath(os.path.dirname(__file__))

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SETTINGS_PATH, 'templates'),

)

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
     'DEFAULT_PERMISSION_CLASSES': (
         'rest_framework.permissions.IsAuthenticated',
     )
}

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
    'location_mgr',
    'periodic',
    'gunicorn',
    'raven.contrib.django.raven_compat',
    'rest_framework',
    'meishi',
    'healthstatus',
    'django_ses',
    'recommendation',
    'stats',
    'commands',
    'email_and_push_infra',
    'base_entity',
    'entity',
    'media_components',
    'polls',
    'taggit',
    'genericm2m',
    'django_filters',
    'polymorphic',
    'rest_framework.authtoken',
    'taganomy',
    'taggit_serializer',
    'rest_auth',
    'rest_auth.registration',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
#    'herald'
)

#django-storage settings

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = 'AKIAJCEZ5MQHG4U2M2UA'
AWS_SECRET_ACCESS_KEY = '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'
AWS_BUCKET_ENV = "-" + RUNENV
AWS_QUERYSTRING_AUTH = False
#Expiry set to 100 years
AWS_QUERYSTRING_EXPIRE = 3153600000
AWS_STORAGE_BUCKET_NAME = 'girnar-image-bucket' + AWS_BUCKET_ENV
S3_URL = 'http://s3.ap-south-1.amazonaws.com/%s' % AWS_STORAGE_BUCKET_NAME
EMAIL_DEFAULT_IMAGE = S3_URL +  "/invites/email_info.png"
DEFAULT_VIDEO_THUMBNAIL = AWS_STORAGE_BUCKET_NAME+ "/thumbnails/no-video-uploaded.gif"

STATIC_DIRECTORY = '/static/'
MEDIA_DIRECTORY = '/media/'


#django-ses Settings
SES_SMTP_USER = 'AKIAJIXICBLUCPSKQPKA'
SES_SMTP_PASS = 'AgHl9hZWrbH51ur6WorLxNJ7ETxb8fmqHg2OUbkVDKrv'
AWS_SES_REGION_NAME = 'us-east-1'
AWS_SES_REGION_ENDPOINT = 'email.us-east-1.amazonaws.com'
EMAIL_BACKEND='django_ses.SESBackend'
#AWS_RETURN_PATH='wizcarder@gmail.com'
AWS_RETURN_PATH='admin@getwizcard.com'
SES_RETURN_PATH='admin@getwizcard.com'
DEFAULT_FROM_EMAIL='admin@getwizcard.com'
#ACCOUNT_EMAIL_VERIFICATION='mandatory'
ACCOUNT_EMAIL_REQUIRED=True
#ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = True
ENABLE_PHONE_LIST_CHECK = False
GIRNAR_ENABLE = True

#ACCOUNT_AUTHENTICATION_METHOD='email'
#LOGIN_REDIRECT_URL = "http://www.getwizcard.com"

REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'userprofile.serializers.UserRegisterSerializer',
}

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



MYLOG = {}
MYLOG['dev'] = {
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
    },
    'loggers': {
        'django': {
            'level':'DEBUG',
            'handlers': ['timed-log-file'],
            'propagate': False,
        },
        'wizserver': {
            'level': 'DEBUG',
            'handlers': ['console', 'watched-log-file'],
            'propagate': False,
        },

    }
}
MYLOG[RUNENV] = MYLOG['dev']
if RUNENV != 'dev':
    MYLOG[RUNENV]['handlers']['sentry'] = {
        'level': 'ERROR',
        'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
    }
    MYLOG[RUNENV]['loggers']['sentry.errors'] = {
        'level': 'ERROR',
        'handlers': ['console'],
        'propagate': False,
    }
    MYLOG[RUNENV]['loggers']['raven'] = {
        'level': 'ERROR',
        'handlers': ['console'],
        'propagate': False,
    }

LOGGING = MYLOG[RUNENV]

APP_ID = 'com.beta.wizcard'
PYAPNS_CONFIG = {
    'HOST': 'http://localhost:7077/',
    'TIMEOUT': 1,                    # OPTIONAL, host timeout in seconds
    'INITIAL': [                      # OPTIONAL, see below
    #  ('com.beta.wizcard', open('./certs/wizcard_ios_apns_dev.pem').read(), 'sandbox'),
    ('com.beta.wizcard', open('./certs/wizcard_ios_apns_production.pem').read(), 'production'),
  ]
}

GCM_API_KEY = 'AAAAFguIzVE:APA91bGovHuuA7-zc7qFAlBuUx6sDPNUqpg-MbH_XlIn-U_QoVJs2MgYKt9ETaVzYI-iEIIRGW5-w7ACJM8cvV6OLAMvOxBwWKxiwDa1ZKr0ssKg8CxUSz0QlW_4IWFtVNK2Pm5zosac'
SHORTEN_API_KEY = 'AIzaSyBiw4HSRUb8VlR5oY0bLuRPTjT2G-fW8qo'
SHORTEN_SERVICE = 'Google'

CELERY_TIMEZONE = TIME_ZONE
# RECOMMENDATION SETTINGS
# In minutes - Interval to check for recommendation for trigger and full
FULL_RECO_GEN_INTERVAL = 5

# Default size for get_recommendations
GET_RECO_SIZE = 10

#Periodic RECO_GEN_INTERVAL
PERIODIC_RECO_GEN_INTERVAL = 1


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = (
    # `allauth` specific authentication methods, such as login by e-mail
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

GIRNAR_ATTENDEES = {
    '+918971546485' : 1,
    "+919884116543" : 1,
	"+919840095748" : 1,
	"+919840615574" : 1,
	"+917200492008" : 1,
	"+918122366748" : 1,
	"+919003368478" : 1,
	"+919840412963" : 1,
	"+917665912960" : 1,
	"+919940193145" : 1,
	"+919444536407" : 1,
	"+919043062489" : 1,
	"+919940412941" : 1,
	"+919840703055" : 1,
	"+919543559807" : 1,
	"+917358647523" : 1,
	"+919444588306" : 1,
	"+919566034963" : 1,
	"+919940429355" : 1,
	"+919566029299" : 1,
	"+919677074256" : 1,
	"+919677047900" : 1,
	"+919543214735" : 1,
	"+918939510287" : 1,
	"+919789093310" : 1,
	"+919940370356" : 1,
	"+918939506459" : 1,
	"+919790750101" : 1,
	"+919380938045" : 1,
	"+918015804740" : 1,
	"+919791093972" : 1,
	"+919840346654" : 1,
	"+919566150360" : 1,
	"+919840455480" : 1,
	"+919003810184" : 1,
	"+919790980320" : 1,
	"+918056116347" : 1,
	"+919444077855" : 1,
	"+919003167264" : 1,
	"+917904768856" : 1,
	"+919884132835" : 1,
	"+919840023840" : 1,
	"+917305622737" : 1,
	"+919791130474" : 1,
	"+918695293974" : 1,
	"+919448219447" : 1,
	"+919566292931" : 1,
	"+919444479396" : 1,
	"+919444452628" : 1,
	"+919444243926" : 1,
	"+919790858579" : 1,
	"+919677230392" : 1,
	"+919884970331" : 1,
	"+919092634223" : 1,
	"+918939124634" : 1,
	"+919840859430" : 1,
	"+919841454564" : 1,
	"+919841137036" : 1,
	"+919500171727" : 1,
	"+919380377148" : 1,
	"+919042590425" : 1,
	"+919176088360" : 1,
	"+919789420043" : 1,
	"+919840394969" : 1,
	"+919840767523" : 1,
	"+919791072224" : 1,
	"+918220847479" : 1,
	"+919003231749" : 1,
	"+919677210117" : 1,
	"+918438543633" : 1,
	"+917845660146" : 1,
	"+919444257715" : 1,
	"+919025034974" : 1,
	"+919677320536" : 1,
	"+918072950639" : 1,
	"+919500525526" : 1,
	"+919092036272" : 1,
	"+919865625947" : 1,
	"+919442327287" : 1,
	"+919443303813" : 1,
	"+919994846807" : 1,
	"+919566680110" : 1,
	"+919626607116" : 1,
	"+919843789500" : 1,
	"+917667403020" : 1,
	"+919629664247" : 1,
	"+919952439903" : 1,
	"+919486258322" : 1,
	"+919442056669" : 1,
	"+919486209074" : 1,
	"+919443831063" : 1,
	"+919629580051" : 1,
	"+919443362660" : 1,
	"+919629636517" : 1,
	"+919442751500" : 1,
	"+919500848545" : 1,
	"+919344100808" : 1,
	"+919047052249" : 1,
	"+919488961797" : 1,
	"+918098260411" : 1,
	"+919944391287" : 1,
	"+919943330944" : 1,
	"+919585570001" : 1,
	"+919042979788" : 1,
	"+919025795337" : 1,
	"+919842110000" : 1,
	"+919443805369" : 1,
	"+917010770137" : 1,
	"+917667641676" : 1,
	"+919543442006" : 1,
	"+919443065530" : 1,
	"+919894075310" : 1,
	"+919443134994" : 1,
	"+919444006168" : 1,
	"+919566778320" : 1,
	"+917708412588" : 1,
	"+919629659789" : 1,
	"+919585099077" : 1,
	"+919344103671" : 1,
	"+919789220375" : 1,
	"+919500712222" : 1,
	"+919369297818" : 1,
	"+919043771344" : 1,
	"+918148594114" : 1,
	"+919344100342" : 1,
	"+919025339629" : 1,
	"+918248218268" : 1,
	"+917867903210" : 1,
	"+917708184351" : 1,
	"+919443969854" : 1,
	"+919003347262" : 1,
	"+919994401101" : 1,
	"+919789577154" : 1,
	"+919442702872" : 1,
	"+919445826705" : 1,
	"+919790346691" : 1,
	"+919791046033" : 1,
	"+918754277772" : 1,
	"+919944377605" : 1,
	"+919443940516" : 1,
	"+919488248438" : 1,
	"+919677380815" : 1,
	"+919345094950" : 1,
	"+919894272428" : 1,
	"+919487046278" : 1,
	"+919043190131" : 1,
	"+918754175806" : 1,
	"+919443475806" : 1,
	"+919791743005" : 1,
	"+919940241936" : 1,
	"+919443132439" : 1,
	"+919443698910" : 1,
	"+919884763020" : 1,
	"+918438444919" : 1,
	"+919047383731" : 1,
	"+919566656708" : 1,
	"+919025336909" : 1,
	"+919486948370" : 1,
	"+919790073304" : 1,
	"+918870586534" : 1,
	"+919443796626" : 1,
	"+919442621705" : 1,
	"+919944863368" : 1,
	"+919533573311" : 1,
	"+919159887903" : 1,
	"+918940206722" : 1,
	"+917598352554" : 1,
	"+919043342286" : 1,
	"+919952283027" : 1,
	"+919994925602" : 1,
	"+918778444040" : 1,
	"+917871477247" : 1,
	"+919442903032" : 1,
	"+918608384840" : 1,
	"+918695699293" : 1,
	"+919443337004" : 1,
	"+917200831707" : 1,
	"+919043495116" : 1,
	"+919994479536" : 1,
	"+919057576191" : 1,
	"+919833184850" : 1,
	"+919076699801" : 1,
	"+919322248798" : 1,
	"+919699324790" : 1,
	"+918108107085" : 1,
	"+919987200277" : 1,
	"+919869721620" : 1,
	"+918082423149" : 1,
	"+919870060567" : 1,
	"+919987062727" : 1,
	"+917045206175" : 1,
	"+919320220218" : 1,
	"+919820454299" : 1,
	"+919324135096" : 1,
	"+919324798263" : 1,
	"+919768181098" : 1,
	"+919320222273" : 1,
	"+919892897023" : 1,
	"+919757211891" : 1,
	"+919987466456" : 1,
	"+917715044101" : 1,
	"+918433666683" : 1,
	"+919220999717" : 1,
	"+919167944951" : 1,
	"+919930778993" : 1,
	"+919323400291" : 1,
	"+917391983109" : 1,
	"+919969288130" : 1,
	"+919867640238" : 1,
	"+919969256210" : 1,
	"+919324107903" : 1,
	"+919892466991" : 1,
	"+919773582650" : 1,
	"+919820431969" : 1,
	"+917678033018" : 1,
	"+919920433221" : 1,
	"+919321195197" : 1,
	"+919867297445" : 1,
	"+919869690779" : 1,
	"+919022689656" : 1,
	"+919323711401" : 1,
	"+919833985699" : 1,
	"+917738390000" : 1,
	"+918879569351" : 1,
	"+917435931914" : 1,
	"+919619781788" : 1,
	"+919821760630" : 1,
	"+919867809422" : 1,
	"+919167362975" : 1,
	"+919820939946" : 1,
	"+919022215861" : 1,
	"+918097500071" : 1,
	"+919930927231" : 1,
	"+919930500672" : 1,
	"+919323372573" : 1,
	"+919028278284" : 1,
	"+919167286977" : 1,
	"+918268011789" : 1,
	"+917738772338" : 1,
	"+919892878999" : 1,
	"+919594132233" : 1,
	"+919773646815" : 1,
	"+919819162577" : 1,
	"+917303839193" : 1,
	"+919819108072" : 1,
	"+919029535372" : 1,
	"+919167032427" : 1,
	"+918087746333" : 1,
	"+919920280712" : 1,
	"+918655713394" : 1,
	"+919892370066" : 1,
	"+919833256197" : 1,
	"+919892592149" : 1,
	"+919730377048" : 1,
	"+917666974866" : 1,
	"+919833181870" : 1,
	"+919975085255" : 1,
	"+919819692592" : 1,
	"+919920296974" : 1,
	"+919167210997" : 1,
	"+919730838099" : 1,
	"+919819576948" : 1,
	"+918446409155" : 1,
	"+918779107310" : 1,
	"+919820102514" : 1,
	"+919322152552" : 1,
	"+919820821398" : 1,
	"+919427110663" : 1,
	"+919377713579" : 1,
	"+919924094423" : 1,
	"+917874564177" : 1,
	"+919824942944" : 1,
	"+919428045019" : 1,
	"+919998427316" : 1,
	"+919925457531" : 1,
	"+919824387338" : 1,
	"+919714985869" : 1,
	"+918488093800" : 1,
	"+917874166764" : 1,
	"+919428495670" : 1,
	"+919429280023" : 1,
	"+919712994243" : 1,
	"+919913003838" : 1,
	"+919408002469" : 1,
	"+918140192909" : 1,
	"+919979862308" : 1,
	"+919409147869" : 1,
	"+919925037179" : 1,
	"+919879082284" : 1,
	"+919328267653" : 1,
	"+919099600400" : 1,
	"+919408286926" : 1,
	"+919427773800" : 1,
	"+919429365652" : 1,
	"+918758223367" : 1,
	"+919586319003" : 1,
	"+919408117780" : 1,
	"+919409407328" : 1,
	"+918488041787" : 1,
	"+919082067458" : 1,
	"+919998718783" : 1,
	"+919408235883" : 1,
	"+919409270256" : 1,
	"+918469415130" : 1,
	"+917600055647" : 1,
	"+919998707755" : 1,
	"+919429012393" : 1,
	"+919033407710" : 1,
	"+919879461876" : 1,
	"+918980005966" : 1,
	"+919979203736" : 1,
	"+919426525330" : 1,
	"+919974714287" : 1,
	"+919408784321" : 1,
	"+917623099999" : 1,
	"+919033706327" : 1,
	"+917874167071" : 1,
	"+919537875697" : 1,
	"+919428668918" : 1,
	"+919449590599" : 1,
	"+918261761950" : 1,
	"+919036506839" : 1,
	"+919844480215" : 1,
	"+919448972855" : 1,
	"+918352250621" : 1,
	"+919632601351" : 1,
	"+917795808910" : 1,
	"+919663196446" : 1,
	"+919632916251" : 1,
	"+919483963864" : 1,
	"+919036414688" : 1,
	"+918553131498" : 1,
	"+919550153570" : 1,
	"+919440548941" : 1,
	"+918500860867" : 1,
	"+919494293345" : 1,
	"+919491455716" : 1,
	"+919441371138" : 1,
	"+919966450001" : 1,
	"+919885347721" : 1,
	"+917744848139" : 1,
	"+917768833133" : 1,
	"+918796607431" : 1,
	"+919960500588" : 1,
	"+919163623214" : 1,
	"+919431127912" : 1,
	"+919836708466" : 1,
	"+919703027162" : 1,
	"+917697960097" : 1,
	"+918989557549" : 1,
	"+919993214371" : 1,
	"+918349895151" : 1,
	"+919636496409" : 1,
	"+919246825959" : 1,
	"+919822409263" : 1,
	"+919000586045" : 1,
	"+919448368046" : 1,
	"+919158666153" : 1,
	"+917773967005" : 1,
	"+918788286473" : 1,
	"+919423583860" : 1,
	"+919448873124" : 1,
	"+918194225403" : 1,
	"+919448924012" : 1,
	"+918330973914" : 1,
	"+919441747401" : 1,
	"+919482400789" : 1,
	"+919533693678" : 1,
	"+919986997110" : 1,
	"+917057501144" : 1,
	"+919480014968" : 1,
	"+919845993003" : 1,
	"+919331808794" : 1,
	"+919414516316" : 1,
	"+919739681160" : 1,
	"+919008880361" : 1,
	"+919611666318" : 1,
	"+918147889537" : 1,
	"+919036414107" : 1,
	"+919986951139" : 1,
	"+919481294260" : 1,
	"+917026591659" : 1,
	"+918520887601" : 1,
	"+919820289147" : 1,
	"+918861210262" : 1,
	"+919036400350" : 1,
	"+919798934510" : 1,
	"+917026870731" : 1,
	"+919404837515" : 1,
	"+919700771662" : 1,
	"+917093299904" : 1,
	"+917259399403" : 1,
	"+918142576700" : 1,
	"+919849386635" : 1,
	"+918328556182" : 1,
	"+918099137608" : 1,
	"+919966841111" : 1,
	"+918560994323" : 1,
	"+919421289059" : 1,
	"+919423285850" : 1,
	"+917875689111" : 1,
	"+917020927805" : 1,
	"+918341721012" : 1,
	"+919642256879" : 1,
	"+919440350000" : 1,
	"+919983433919" : 1,
	"+918424982619" : 1,
	"+919595622269" : 1,
	"+919028647774" : 1,
	"+917567707247" : 1,
	"+919890119198" : 1,
	"+919755748825" : 1,
	"+918055265434" : 1,
	"+919579282482" : 1,
	"+919036493593" : 1,
	"+919713350025" : 1,
	"+919908242621" : 1,
	"+918106242403" : 1,
	"+919985822500" : 1,
	"+919700142900" : 1,
	"+917680013217" : 1,
	"+919866025148" : 1,
	"+919886746605" : 1,
	"+918003385338" : 1,
	"+918149250580" : 1,
	"+918884087107" : 1,
	"+919301222160" : 1,
	"+919907030936" : 1,
	"+919424591256" : 1,
	"+918762068410" : 1,
	"+919060988888" : 1,
	"+919993802008" : 1,
	"+919998856788" : 1,
	"+919880049490" : 1,
	"+919448373787" : 1,
	"+919035100271" : 1,
	"+919822260684" : 1,
	"+917981813716" : 1,
	"+919420697910" : 1,
	"+919822494838" : 1,
	"+919916971641" : 1,
	"+917276005228" : 1,
	"+918073765265" : 1,
	"+919886948148" : 1,
	"+919490315200" : 1,
	"+919860773020" : 1,
	"+917386823404" : 1,
	"+917207579105" : 1,
	"+918424018178" : 1,
	"+917875606066" : 1,
	"+918247499462" : 1,
	"+918555014645" : 1,
	"+917346747109" : 1,
	"+918308643842" : 1,
	"+919987886257" : 1,
	"+919320752287" : 1,
	"+918087307906" : 1,
	"+918976382654" : 1,
	"+918291683166" : 1,
	"+919833652636" : 1,
	"+919594887778" : 1,
	"+919892175587" : 1,
	"+919833838744" : 1,
	"+918879313435" : 1,
	"+918879220540" : 1,
	"+919833579531" : 1,
	"+919969429431" : 1,
	"+919867861509" : 1,
	"+919029020219" : 1,
	"+919699995563" : 1,
	"+919769853484" : 1,
	"+919664168564" : 1,
	"+919987309439" : 1,
	"+917208887796" : 1,
	"+919819125253" : 1,
	"+919820456509" : 1,
	"+919619644796" : 1,
	"+918667740235" : 1,
	"+919427471775" : 1,
	"+919176364790" : 1,
	"+919043678314" : 1,
	"+918879912165" : 1,
	"+919967746350" : 1,
	"+919825074889" : 1,
	"+919566083420" : 1,
	"+918939324000" : 1,
	"+919500056578" : 1,
	"+919820212502" : 1,
	"+919894210395" : 1,
	"+919972778838" : 1,
	"+918141941818" : 1,
	"+919894120246" : 1,
	"+918050869414" : 1,
	"+919844244552" : 1,
	"+919167227577" : 1,
	"+917977289336" : 1,
	"+919833065165" : 1,
	"+919665364777" : 1,
	"+919324751128" : 1,
	"+919771123611" : 1,
	"+919428243580" : 1,
	"+918080591291" : 1,
	"+919221660006" : 1,
	"+919987357575" : 1,
	"+919930748618" : 1,
	"+919930673833" : 1,
	"+919867407314" : 1,
	"+917425901606" : 1,
	"+919967374078" : 1,
	"+919879504482" : 1,
	"+919979253993" : 1,
	"+919016161657" : 1,
	"+918733005251" : 1,
	"+919428213678" : 1,
	"+919558141541" : 1,
	"+919884682685" : 1,
	"+919820695028" : 1,
	"+919879121100" : 1,
	"+919833641940" : 1,
	"+919177961411" : 1,
	"+919494421683" : 1,
	"+919460052599" : 1,
	"+919840311073" : 1,
	"+919677693274" : 1,
	"+919176585100" : 1,
	"+919586194126" : 1,
	"+919482066483" : 1,
	"+919884415358" : 1,
	"+919872016191" : 1,
	"+919206136020" : 1,
    "+919663638243" : 1,
    "+919930576007" : 1,
    "+919884237486" : 1,"
}
