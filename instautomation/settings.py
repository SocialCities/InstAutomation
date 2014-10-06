import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'jqu*5*!e&epxpql&fgu9fa%3o#kh5f+=m8cf^fwve5n*)@e7y)'

DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_auth',
    'accesso',
    'instagram_like',
    'instagram_follow',
    'djcelery',
    'debug',
    'statistiche',
    'bootstrap3',
    'pagamenti',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'instautomation.middleware.BetaMiddleware',
)

ROOT_URLCONF = 'instautomation.urls'

WSGI_APPLICATION = 'instautomation.wsgi.application'

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
#}

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
		'NAME': 'instadb',                      # Or path to database file if using sqlite3.
		# The following settings are not used with sqlite3:
		'USER': 'instauser',
		'PASSWORD': 'Ottimo310188',
		'HOST': 'localhost',                      # Empty for localhost through domain sockets or           '127.0.0.1' for localhost through TCP.
		'PORT': '',                      # Set to empty string for default.
		}
	}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Rome'

USE_I18N = True

USE_L10N = True

USE_TZ = True

#Production
#STATIC_URL = '/static/'
#STATIC_ROOT = '/webapps/static'

#Dev - Locale
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    '/home/riccardo/Scrivania/InstaTrezzi/static/',
)

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.contrib.instagram.InstagramBackend',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_ENABLED_BACKENDS = ('instagram')

#Dev - Locale
INSTAGRAM_CLIENT_ID = '9866db39f3924bf981581de816d60607'
INSTAGRAM_CLIENT_SECRET = 'e42bb095bdc6494aa351872ea17581ac'

#Production
#INSTAGRAM_CLIENT_ID = '2b1ae8cc46c744708b86204315588912'
#INSTAGRAM_CLIENT_SECRET = 'a8a4ff3b196a424b9de2c42d8d781a41'


INSTAGRAM_REDIRECT_URI = "http://instautomation.com/complete/instagram/"

DEFAULT_HOST = "http://instautomation.com"

LOGIN_URL          = '/login'
LOGIN_REDIRECT_URL = '/access'
LOGIN_ERROR_URL    = '/login-error/'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

INSTAGRAM_AUTH_EXTRA_ARGUMENTS = {'scope': 'likes comments relationships'}

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
           ### MAIL ###
    'filters': {
        'special': {
            '()': 'django.utils.log.RequireDebugFalse',
            #'foo': 'bar',
        },
    },
           ### MAIL ###
    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
            },
                 ### MAIL ###
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
            'filters': ['special']
        },
                 ### MAIL ###
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '../instautomation/debug.log',
            'formatter': 'verbose'
            },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '../instautomation/error.log',
            'formatter': 'verbose'
            },
        },
    'loggers': {
        'django': {
            'handlers': ['debug_file', 'error_file','mail_admins'],
            'level': 'INFO',
            'propagate': True,
            },
        }
    }


#Dev - Locale
IP_LOCALE = '79.49.55.89'

#Production
IP_LOCALE = '178.62.48.51'

### Configurazione Email ###
EMAIL_USE_TLS = True 
EMAIL_HOST = 'mail.instautomation.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'admindjango'
EMAIL_HOST_PASSWORD = '5autobus'
DEFAULT_FROM_EMAIL = 'admindjango@instautomation.com'

###









