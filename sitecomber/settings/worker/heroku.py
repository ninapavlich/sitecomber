from sitecomber.settings.worker.base import *

if 'file' in LOGGING['handlers']:
    del LOGGING['handlers']['file']

LOGGING['loggers']['django']['handlers'] = ['console']
LOGGING['loggers']['root']['handlers'] = ['console']
