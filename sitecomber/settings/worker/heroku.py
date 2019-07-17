from sitecomber.settings.worker.base import *


del LOGGING['handlers']['file']

LOGGING['loggers']['django']['handlers'] = ['console']
LOGGING['loggers']['root']['handlers'] = ['console']
