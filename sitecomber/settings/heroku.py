from sitecomber.settings.base import *

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
ALLOWED_HOSTS = [env('APP_HOST_NAME')]
CORS_ORIGIN_WHITELIST = (
    env('APP_HOST_NAME')
)
CSRF_TRUSTED_ORIGINS = (
    env('APP_HOST_NAME')
)


del LOGGING['handlers']['file']

LOGGING['loggers']['django']['handlers'] = ['console']
LOGGING['loggers']['root']['handlers'] = ['console']
