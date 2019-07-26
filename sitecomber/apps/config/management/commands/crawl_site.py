import logging
import time

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from sitecomber.apps.config.models import Site

logger = logging.getLogger('django')


class Command(BaseCommand):
    """
    Example Usage:

    Load 10 urls on the site with primary key 1:
    python manage.py crawl_site 1 10

    Load 10 urls on all sites:
    python manage.py crawl_site -1 10

    """

    help = 'Crawl Site'

    def add_arguments(self, parser):

        parser.add_argument('site_pk', nargs='+', type=int)
        parser.add_argument('load_batch_size', nargs='+', type=int)

    def handle(self, *args, **options):

        start = time.time()
        site_pk = int(options['site_pk'][0])
        load_batch_size = int(options['load_batch_size'][0])

        if site_pk == -1:
            logger.info("Going to crawl %s urls in all sites" % (load_batch_size))
            for site in Site.objects.all():
                site.parse_sitemap()
                site.crawl(load_batch_size)

        else:
            logger.info("Going to crawl %s urls in site %s" % (load_batch_size, site_pk))
            try:
                site = Site.objects.get(pk=site_pk)
            except ObjectDoesNotExist:
                logger.error(u"Could not find site with primary key = %s" % (site_pk))
                return

            site.parse_sitemap()
            site.crawl(load_batch_size)

        logger.warn("Crawling took %s seconds" % (time.time() - start))
