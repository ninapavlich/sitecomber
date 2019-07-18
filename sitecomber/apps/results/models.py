import logging
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property

import requests

from sitecomber.apps.shared.models import BaseMetaData, BaseURL, BaseHeader, BaseRequest, BaseResponse, BaseTestResult
from sitecomber.apps.shared.utils import LinkParser

logger = logging.getLogger('django')


class RequestHeader(BaseHeader):
    parent = models.ForeignKey(
        'results.PageRequest',
        null=False,
        on_delete=models.CASCADE
    )


class ResponseHeader(BaseHeader):
    parent = models.ForeignKey(
        'results.PageResponse',
        null=False,
        on_delete=models.CASCADE
    )


class PageResponse(BaseMetaData, BaseResponse):
    """
    Represents a single request and response from the server
    """

    response_header_model = ResponseHeader

    request = models.ForeignKey(
        'results.PageRequest',
        on_delete=models.CASCADE
    )
    redirected_from = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    load_start_time = models.DateTimeField(blank=True, null=True)
    load_end_time = models.DateTimeField(blank=True, null=True)

    text_content = models.TextField(blank=True, null=True)

    def __str__(self):
        return u'%s at %s' % (self.response_url, self.load_end_time)

    @classmethod
    def parse_response(cls, request, redirected_from, response):
        r = PageResponse(
            response_url=response.url,
            status_code=response.status_code,
            request=request,
            load_start_time=request.load_start_time,
            load_end_time=request.load_start_time + response.elapsed,
            redirected_from=redirected_from
        )
        if response.text:
            r.text_content = response.text

        if response.headers.get('content-type'):
            r.content_type = response.headers.get('content-type')
        else:
            logger.warn(u"Response from URL %s missing the content-type header" % (response.url))

        if response.headers.get('content-length'):
            r.content_length = response.headers.get('content-length')
        else:
            logger.warn(u"Response from URL %s missing the content-length header" % (response.url))

        try:
            r.save()
            r.create_response_headers(response.headers)
            return r
        except Exception as e:
            logger.error(u"Error saving response for URL %s: %s" % (response.url, e))

    @classmethod
    def parse_error_response(cls, request, redirected_from, error_message):
        r = PageResponse(
            response_url=request.request_url,
            status_code=0,
            text_content=error_message,
            request=request,
            load_start_time=request.load_start_time,
            load_end_time=request.load_start_time,
            redirected_from=redirected_from
        )
        try:
            r.save()
            return r
        except Exception as e:
            logger.error(u"Error saving error response for URL %s - %s: %s" % (request.request_url, error_message, e))


class PageRequest(BaseMetaData, BaseRequest):
    """
    Represents an entire chain of requests and responses until finally
    a non-redirecting response is given
    """
    request_header_model = RequestHeader

    page_result = models.ForeignKey(
        'results.PageResult',
        on_delete=models.CASCADE
    )
    response = models.ForeignKey(
        'results.PageResponse',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    load_start_time = models.DateTimeField(blank=True, null=True)
    load_end_time = models.DateTimeField(blank=True, null=True)
    retain = models.BooleanField(default=False)

    def __str__(self):
        return u'%s at %s' % (self.request_url, self.load_start_time)

    def load(self):
        self.load_start_time = timezone.now()
        self.method = BaseRequest.METHOD_GET
        self.request_url = self.page_result.url
        self.save()

        request_headers = {'user-agent': self.page_result.site_domain.site.get_user_agent()}
        self.create_request_headers(request_headers)

        response = None
        error_message = None
        previous_item = None
        try:
            response = requests.get(
                self.page_result.url,
                headers=request_headers,
                timeout=self.page_result.site_domain.site.get_max_timeout_seconds()
            )
        except requests.exceptions.ConnectionError as e:
            error_message = "ERROR: Connection Error when trying to load %s: %s" % (self.page_result.url, e)
        except requests.exceptions.Timeout as e:
            error_message = "ERROR: Timeout when trying to load %s: %s" % (self.page_result.url, e)
        except requests.exceptions.RequestException as e:
            error_message = "ERROR: Request Exception when trying to load %s: %s" % (self.page_result.url, e)
        except requests.exceptions.TooManyRedirects as e:
            error_message = "ERROR: Too many redirects when trying to load %s: %s" % (self.page_result.url, e)

        self.load_end_time = timezone.now()

        # If this is an internal page, then parse its contents:
        if response and self.page_result.is_internal:
            parser = LinkParser(self.page_result.site_domain.url, self.page_result.site_domain.site.domains, self.page_result.site_domain.site.ignored_query_params)
            parser.feed(response.text)

            for link in parser.internal_links:
                self.page_result.site_domain.handle_link(link, self.page_result, True)

            for link in parser.external_links:
                self.page_result.site_domain.handle_link(link, self.page_result, False)

            for item in response.history:
                previous_item = PageResponse.parse_response(self, previous_item, item)

        if error_message:
            self.response = PageResponse.parse_error_response(self, previous_item, error_message)
            logger.error(error_message)
        else:
            self.response = PageResponse.parse_response(self, previous_item, response)

        self.save()


class PageResult(BaseMetaData, BaseURL):

    site_domain = models.ForeignKey(
        'config.SiteDomain',
        on_delete=models.CASCADE
    )
    last_load_time = models.DateTimeField(blank=True, null=True)
    incoming_links = models.ManyToManyField('self', symmetrical=False, related_name="page_incoming_links",)
    outgoing_links = models.ManyToManyField('self', symmetrical=False, related_name="page_outgoing_links",)

    is_sitemap = models.BooleanField(default=False)
    is_root = models.BooleanField(default=False)
    is_internal = models.BooleanField(default=True)

    def load(self):
        logger.info(u"Loading %s" % (self))

        # First clean old records
        old_records = PageRequest.objects.filter(page_result=self).exclude(retain=True).order_by('-created')
        for old_record in old_records[settings.DEFAULT_MAINTAIN_PREVIOUS_RECORD_COUNT:]:
            old_record.delete()

        result = PageRequest(page_result=self)
        result.save()
        result.load()

        self.last_load_time = timezone.now()
        self.save()

    @cached_property
    def latest_request(self):
        return self.pagerequest_set.order_by('-created').first()

    class Meta:
        ordering = ['site_domain', 'url']


class SiteTestResult(BaseMetaData, BaseTestResult):

    site = models.ForeignKey(
        'config.Site',
        on_delete=models.CASCADE
    )


class SiteDomainTestResult(BaseMetaData, BaseTestResult):

    site_domain = models.ForeignKey(
        'config.SiteDomain',
        on_delete=models.CASCADE
    )


class PageTestResult(BaseMetaData, BaseTestResult):

    page = models.ForeignKey(
        'results.PageResult',
        on_delete=models.CASCADE
    )
