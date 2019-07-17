from sitecomber.settings.base import *


# -- Default Settings:
WORKER_NAME = "SiteComber Worker"
WORKER_ID = "sitecomber-worker"

WORKER_DATABASE_REFRESH_FREQUENCY = 60 * 5

PID_FILE = env("WORKER_PID_FILE", default=os.path.join(BASE_DIR, '%s.pid' % (WORKER_ID)))
LOG_FILE = env("WORKER_LOG_FILE", default=os.path.join(BASE_DIR, 'logs/%s.log' % (WORKER_ID)))


# LOGGING
# -----------------------------------------------------------------------------

LOGGING_CONFIG = 'logging.config.dictConfig'
LOGGING['loggers'][WORKER_ID] = {
    'handlers': ['console', 'file'],
    'level': 'WARNING',
    'propagate': True,
}


if DEBUG:
    LOGGING['loggers'][WORKER_ID]['level'] = 'INFO'
    LOGGING['loggers']['django']['level'] = 'INFO'
    LOGGING['loggers']['root']['level'] = 'INFO'
    LOGGING['handlers']['console']['level'] = 'INFO'
    LOGGING['handlers']['file']['level'] = 'INFO'

LOAD_BATCH_SIZE = int(env('LOAD_BATCH_SIZE', default=10))
