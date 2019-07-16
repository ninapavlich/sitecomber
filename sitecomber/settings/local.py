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
