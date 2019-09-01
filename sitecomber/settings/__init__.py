import environ

root = environ.Path(__file__) - 3  # three folder back (/a/b/c/ - 3 = /)
env = environ.Env()  # set default values and casting
environ.Env.read_env(env_file=root('.env'))
print(root('.env'))
SECRET_KEY = env('SECRET_KEY')

ENVIRONMENT = env('ENVIRONMENT', default='local')

exec('from sitecomber.settings.%s import *' % ENVIRONMENT)
