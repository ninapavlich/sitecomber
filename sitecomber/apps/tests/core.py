import logging
import json

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

            status = PageTestResult.STATUS_WARNING
            if status_code == 200:
                status = PageTestResult.STATUS_SUCCESS
                message = 'Okay'
            elif (status_code == -1) or (status_code >= 300 and status_code < 600):
                status = PageTestResult.STATUS_ERROR
                message = 'Error loading %s returned error code %s' % (page.url, status_code)
            else:
                message = 'Warning loading %s returned unexpected code %s' % (page.url, status_code)

            try:
                r, created = PageTestResult.objects.get_or_create(
                    page=page,
                    test=self.class_path
                )
                data = {
                    'status_code': status_code
                }
                try:
                    r.data = json.dumps(data, sort_keys=True, indent=2)
                except Exception as e:
                    logger.error(u"Error dumping JSON data: %s: %s" % (data, e))
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
            if outgoing_link.latest_request and outgoing_link.latest_request.response:
                status_code = outgoing_link.latest_request.response.status_code
                if (status_code == -1) or (status_code >= 300 and status_code < 600):
                    broken_outgoing_links.append(outgoing_link.url)

        broken_link_count = len(broken_outgoing_links)
        status = PageTestResult.STATUS_SUCCESS if broken_link_count == 0 else PageTestResult.STATUS_ERROR
        message = 'Okay' if broken_link_count == 0 else 'Found %s broken link(s): %s' % (broken_link_count, u", ".join(broken_outgoing_links))

        try:
            r, created = PageTestResult.objects.get_or_create(
                page=page,
                test=self.class_path
            )
            r.data = broken_outgoing_links  # TODO -- perhaps more structure info
            data = {
                'broken_outgoing_links': broken_outgoing_links
            }
            try:
                r.data = json.dumps(data, sort_keys=True, indent=2)
            except Exception as e:
                logger.error(u"Error dumping JSON data: %s: %s" % (data, e))

            r.message = message
            r.status = status
            r.save()
        except MultipleObjectsReturned as e:
            logger.error("MultipleObjectsReturned when trying to create PageTestResult for test %s on page %s: %s" % (self, page, e))
