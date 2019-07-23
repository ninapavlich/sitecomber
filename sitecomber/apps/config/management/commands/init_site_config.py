import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from sitecomber.apps.config.models import Site, SiteDomain, SiteTestSetting
from sitecomber.apps.shared.utils import get_test_choices

logger = logging.getLogger('django')


class Command(BaseCommand):
    """
    Example Usage:

    python manage.py init_site_config

    """

    help = 'Initialize Site Config'

    def handle(self, *args, **options):

        starting_url = settings.STARTING_URL
        if not starting_url:
            starting_url = input("Please enter starting URL: ")

        validate = URLValidator()
        try:
            validate(starting_url)
        except ValidationError:
            print("Please enter a fully qualified URL")
            return

        user = get_user_model().objects.all().first()
        if not user:
            print("Please create an admin user first using the command: python manage.py createsuperuser")
            return

        site, site_created = Site.objects.get_or_create(
            owner=user,
            title=starting_url
        )
        print("Initializing site settings for %s" % (starting_url))

        site_domain, site_domain_created = SiteDomain.objects.get_or_create(
            site=site,
            url=starting_url
        )

        test_choices = get_test_choices()
        for test_choice in test_choices:
            site_test_setting, site_test_setting_created = SiteTestSetting.objects.get_or_create(
                site=site,
                test=test_choice[0]
            )
            print("-- enabled %s" % test_choice[0])

        print("Site settings initialized for %s. You may configure it at /admin/config/site/%s/change/" % (site, site.pk))
