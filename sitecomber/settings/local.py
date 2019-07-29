from sitecomber.settings.base import *

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
INTERNAL_IPS = ['127.0.0.1', 'localhost']

CORS_ORIGIN_WHITELIST = (
    'localhost:8080',
    '127.0.0.1:8000'
)
CSRF_TRUSTED_ORIGINS = (
    'localhost:8080',
    '127.0.0.1:8000'
)

LOGGING['handlers']['console']['level'] = 'INFO'
LOGGING['handlers']['file']['level'] = 'INFO'
LOGGING['loggers']['django']['level'] = 'INFO'
LOGGING['loggers']['root']['level'] = 'INFO'

# # Needed to create Django permission records w/o triggering a
# # "too many SQL variables" error, see: https://code.djangoproject.com/ticket/17788
# from django.db.backends import sqlite3
# sqlite3.base.DatabaseFeatures.can_combine_inserts_with_and_without_auto_increment_pk = False
