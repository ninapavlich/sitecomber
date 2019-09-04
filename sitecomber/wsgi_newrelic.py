import os
import environ

from django.core.wsgi import get_wsgi_application
import newrelic.agent


root = environ.Path(__file__) - 2
env = environ.Env()
environ.Env.read_env(env_file=root('.env'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sitecomber.settings")

NEW_RELIC_CONFIG_FILE = env('NEW_RELIC_CONFIG_FILE', default=None)
if NEW_RELIC_CONFIG_FILE:
    newrelic.agent.initialize(NEW_RELIC_CONFIG_FILE)

    application = get_wsgi_application()
    application = newrelic.agent.wsgi_application()(application)

else:
    print("dont use new relic!")
    application = get_wsgi_application()
