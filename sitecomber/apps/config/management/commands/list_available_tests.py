from django.core.management.base import BaseCommand

from sitecomber.apps.shared.utils import get_test_choices


class Command(BaseCommand):
    """
    Example Usage:

    python manage.py list_available_tests

    """

    help = 'Display Available Tests'

    def handle(self, *args, **options):

        print("Going to list available tests:")
        tests = get_test_choices()
        for test in tests:
            print(u"- %s" % (test[0]))

        print("If you have added a test and don't see it in the list above, make sure the class is available to the Python executable.")
