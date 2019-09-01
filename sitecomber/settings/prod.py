from sitecomber.settings.base import *

DEBUG = False

#CSRF_COOKIE_SECURE = True
#SESSION_COOKIE_SECURE = True
#SECURE_SSL_REDIRECT = True
ALLOWED_HOSTS = ['35.160.26.81', 'sitecomber.ninalp.com']
CORS_ORIGIN_WHITELIST = ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS = ALLOWED_HOSTS


STATIC_ROOT = '/srv/sitecomber/static/'
MEDIA_ROOT = '/srv/sitecomber/media/'
