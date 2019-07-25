import os
import tempfile
import zipfile
import logging
import shutil

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
# from django.core.files.base import ContentFile
# from django.conf import settings
from django.utils import timezone

from sitecomber.apps.config.models import Site

logger = logging.getLogger('django')


class Command(BaseCommand):
    """
    Example Usage:

    Download all pages in site with primary key 1:
    python manage.py archive_site_pages 1

    """

    help = 'Archive Site Pages'

    def add_arguments(self, parser):

        parser.add_argument('site_pk', nargs='+', type=int)

    def handle(self, *args, **options):

        site_pk = int(options['site_pk'][0])

        if site_pk == -1:
            logger.info("Going to archive all sites")
            for site in Site.objects.all():
                self.download_site(site)

        else:
            logger.info("Going to archive site %s" % (site_pk))
            try:
                site = Site.objects.get(pk=site_pk)
            except ObjectDoesNotExist:
                logger.error(u"Could not find site with primary key = %s" % (site_pk))
                return

            self.download_site(site)

    def download_site(self, site):

        # Set Up Temp Directory for Placing Archived Files In To:
        temp_dirpath = tempfile.mkdtemp()

        for page_result in site.page_results:
            if page_result.latest_response:

                # if page_result.screenshot:
                #     screenshot_file = ContentFile(page_result.screenshot.read())
                #     head, tail = os.path.split(page_result.screenshot.name)

                page_file_target = os.path.join(temp_dirpath, page_result.latest_response.archive_filename)
                if 'text' in page_result.latest_response.content_type:
                    write_to_file(page_file_target, page_result.latest_response.text_content)

                else:
                    # TODO -- download and store binary data
                    pass

        # TODO -- zip directory is not maintaining the folder structure
        # ZIP Temp directory and save it in the archive directory
        output_path = "%s-archive-%s" % (site.title, timezone.now().strftime("%Y-%m-%d_%H-%M"))
        output_zip = "%s.zip" % (output_path)
        zipf = zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED)
        zipdir(temp_dirpath, zipf, output_path)
        zipf.close()

        # Delete old temp directory
        shutil.rmtree(temp_dirpath)


def write_to_file(filename, content, mode='w'):
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    with open(filename, mode) as file:
        file.write(content)
        file.close()


def zipdir(path, ziph, arc_dir):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            arc_file_name = os.path.join(arc_dir, file)
            ziph.write(file_path, arcname=arc_file_name)
