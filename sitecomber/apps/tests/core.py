import logging
import json

from django.core.exceptions import MultipleObjectsReturned

from sitecomber.apps.shared.interfaces import BaseSiteTest

logger = logging.getLogger('django')


class PageUpTest(BaseSiteTest):
    """
    This test checks the status code of each page. If the status code is 200,
    then the page is working. If the status code is a valid error code from
    300-600, or there is an HTTP error when loading the page, then it is
    failing. If we receive some other non-standard error code, then there will
    be a warning.
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
    """
    This test checks if there are any broken links on a given page. If a link
    on the page returns a status code 200, then it is considered working. If a
    link returns a valid error code from 300-600, or there is an HTTP error
    when loading the link, then it is considered broken. If a page returns some
    other non-standard error, then it will display a warning.
    """

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
