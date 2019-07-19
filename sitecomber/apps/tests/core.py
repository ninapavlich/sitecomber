import logging

from django.core.exceptions import MultipleObjectsReturned

from sitecomber.apps.shared.interfaces import BaseSiteTest

logger = logging.getLogger('django')


class PageUpTest(BaseSiteTest):
    """
    Is failing when a page is broken
    """

    def on_page_parsed(self, page):
        from sitecomber.apps.results.models import PageTestResult

        if page.latest_request and page.latest_request.response:
            status_code = page.latest_request.response.status_code

            status = PageTestResult.STATUS_SUCCESS if status_code == 200 else PageTestResult.STATUS_ERROR
            message = 'Okay' if status_code == 200 else 'Error loading %s - Returned code %s' % (page.url, status_code)

            try:
                r, created = PageTestResult.objects.get_or_create(
                    page=page,
                    test=self.class_path
                )
                r.data = status_code  # TODO -- perhaps more structure info
                r.message = message
                r.status = status
                r.save()
            except MultipleObjectsReturned as e:
                logger.error("MultipleObjectsReturned when trying to create PageTestResult for test %s on page %s: %s" % (self, page, e))


class BrokenOutgoingLinkTest(BaseSiteTest):

    def on_page_parsed(self, page):

        # Only apply to internal pages
        if not page.is_internal:
            return

        from sitecomber.apps.results.models import PageTestResult

        broken_outgoing_links = []
        for outgoing_link in page.outgoing_links.all():
            if outgoing_link.latest_request and outgoing_link.latest_request.response and outgoing_link.latest_request.response.status_code != 200:
                broken_outgoing_links.append(outgoing_link.url)

        broken_link_count = len(broken_outgoing_links)
        status = PageTestResult.STATUS_SUCCESS if broken_link_count == 0 else PageTestResult.STATUS_ERROR
        message = 'Okay' if broken_link_count == 0 else 'Found %s broken link(s) on %s' % (broken_link_count, page.url)

        try:
            r, created = PageTestResult.objects.get_or_create(
                page=page,
                test=self.class_path
            )
            r.data = broken_outgoing_links  # TODO -- perhaps more structure info
            r.message = message
            r.status = status
            r.save()
        except MultipleObjectsReturned as e:
            logger.error("MultipleObjectsReturned when trying to create PageTestResult for test %s on page %s: %s" % (self, page, e))
