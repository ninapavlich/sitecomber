"""
Django settings for sitecomber project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import environ

root = environ.Path(__file__) - 3  # three folder back (/a/b/c/ - 3 = /)
env = environ.Env()  # set default values and casting
environ.Env.read_env(env_file=root('.env'))

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), os.pardir))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(env('DEBUG', default=False))

ALLOWED_HOSTS = []

SITE_TITLE = env('SITE_TITLE', default="SiteComber")

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)19s [%(levelname)s] %(pathname)s:%(lineno)d %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': env('LOG_FILE', default=os.path.join(BASE_DIR, 'logs/django.log')),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'default'
        },

    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'root': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
        }
    },
}


INSTALLED_APPS = [

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Admin helpers
    'dal',
    'dal_select2',
    'ckeditor',
    'django_list_wrestler',

    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'encrypted_model_fields',

    # Application components
    'sitecomber.apps.shared',
    'sitecomber.apps.config',
    'sitecomber.apps.results'
]


if DEBUG:
    INSTALLED_APPS += [
        'debug_toolbar',
    ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]

ROOT_URLCONF = 'sitecomber.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'sitecomber', 'apps', 'shared', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sitecomber.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    # Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ
    'default': env.db(),
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_TZ = True
TIME_ZONE = env('TIME_ZONE', default='America/New_York')

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

STATIC_URL = '/static/'
STATIC_ROOT = env('STATIC_ROOT', default=None)
STATICFILES_LOCATION = 'static'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'sitecomber', 'static'),
)

# Uploads
MEDIA_ROOT = env("MEDIA_ROOT", default=os.path.join(
    BASE_DIR, 'uploads/sitecomber/'))
MEDIA_URL = env("MEDIA_URL", default='/uploads/')

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'


# Third-party settings
ONE_HOUR = 60 * 60
API_CACHE_DURATION = int(env('API_CACHE_DURATION', default=ONE_HOUR))


# Django Rest Framework
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',)
}


# WYSIWYG Editor
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Basic',
        'toolbar_Basic': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList'],
            ['RemoveFormat', 'Source']
        ]
    }
}


# Sitecomber defaults
DEFAULT_USER_AGENT = env('DEFAULT_USER_AGENT', default='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:68.0) Gecko/20100101 Firefox/68.0 Sitecomber')
DEFAULT_MAX_REDIRECTS = int(env('DEFAULT_MAX_REDIRECTS', default=6))
DEFAULT_MAX_TIMEOUT_SECONDS = int(env('DEFAULT_MAX_TIMEOUT_SECONDS', default=15))
DEFAULT_SITEMAP_URL = 'sitemap.xml'
