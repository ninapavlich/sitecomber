import logging
import time


from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from sitecomber.apps.config.models import Site
from sitecomber.apps.shared.utils import log_memory

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

        log_memory('1. Starting command')

        if site_pk == -1:
            logger.info("Going to crawl %s urls in all sites" % (load_batch_size))
            for site in Site.objects.all():
                log_memory('2. Before parsing')
                site.parse_sitemap()
                log_memory('3. After parsing / Before crawling')
                site.crawl(load_batch_size)
                log_memory('4. After crawling')

        else:
            logger.info("Going to crawl %s urls in site %s" % (load_batch_size, site_pk))
            try:
                site = Site.objects.get(pk=site_pk)
            except ObjectDoesNotExist:
                logger.error(u"Could not find site with primary key = %s" % (site_pk))
                return

            log_memory('2. Before parsing')
            site.parse_sitemap()
            log_memory('3. After parsing / Before crawling')
            site.crawl(load_batch_size)
            log_memory('4. After crawling')

        logger.info("Crawling took %s seconds" % (time.time() - start))

        log_memory('5. Ending command')
