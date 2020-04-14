import logging

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from sitecomber.apps.results.models import PageResult

logger = logging.getLogger('django')


class Command(BaseCommand):
    """
    Example Usage:

    Load and parse page result with primary key 1:
    python manage.py crawl_page 1

    """

    help = 'Crawl Site'

    def add_arguments(self, parser):
        parser.add_argument('page_result_pk', nargs='+', type=int)

    def handle(self, *args, **options):

        page_result_pk = int(options['page_result_pk'][0])

        logger.info("Going to load page %s" % (page_result_pk))
        try:
            page = PageResult.objects.get(pk=page_result_pk)
        except ObjectDoesNotExist:
            logger.error(u"Could not find page result with primary key = %s" % (page_result_pk))
            return

        page.load()
        tests = page.site_domain.site.tests

        for test in tests:
            test.setUp()
            test.page_parsed(page)
            test.tearDown()
