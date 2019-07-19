import logging

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from sitecomber.apps.config.models import Site

logger = logging.getLogger('django')


class Command(BaseCommand):
    """
    Example Usage:

    Re-run tests on a given site:
    python manage.py rerun_tests 1

    """

    help = 'Crawl Site'

    def add_arguments(self, parser):
        parser.add_argument('site_pk', nargs='+', type=int)

    def handle(self, *args, **options):

        site_pk = int(options['site_pk'][0])

        logger.info("Going to re-run tests on site %s" % (site_pk))
        try:
            site = Site.objects.get(pk=site_pk)
        except ObjectDoesNotExist:
            logger.error(u"Could not find site with primary key = %s" % (site_pk))
            return

        site.parse_sitemap()
        tests = site.tests
        pages = site.page_results
        for page in pages:
            logger.info("- Running tests on %s" % (page))
            for test in tests:
                test.page_parsed(page)
