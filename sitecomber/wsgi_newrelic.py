import os
import environ

from django.core.wsgi import get_wsgi_application
import newrelic.agent


root = environ.Path(__file__) - 2
env = environ.Env()
environ.Env.read_env(env_file=root('.env'))


NEW_RELIC_LICENSE_KEY = env('NEW_RELIC_LICENSE_KEY', default=None)

if NEW_RELIC_LICENSE_KEY:
    NEW_RELIC_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'newrelic.ini'))
    NEW_RELIC_FILE.replace("{{license_key}}", NEW_RELIC_LICENSE_KEY)
    newrelic.agent.initialize(NEW_RELIC_FILE)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sitecomber.settings")


if NEW_RELIC_LICENSE_KEY:
    application = get_wsgi_application()
    application = newrelic.agent.wsgi_application()(application)

else:
    application = get_wsgi_application()
