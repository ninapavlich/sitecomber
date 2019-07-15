from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist


from sitecomber.apps.config.models import Site


class Command(BaseCommand):
    help = 'Parse Site'

    def add_arguments(self, parser):
        parser.add_argument('site_pk', nargs='+', type=int)
        # parser.add_argument('--example_bool', action='store_true', default=False)

    def handle(self, *args, **options):

        site_pk = int(options['site_pk'][0])

        try:
            site = Site.objects.get(pk=site_pk)
        except ObjectDoesNotExist:
            print(u"Could not find site with primary key = %s" % (site_pk))
            return

        site.crawl()
