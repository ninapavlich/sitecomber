import logging
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.text import Truncator


from sitecomber.apps.shared.models import BaseMetaData, BaseURL, BaseRequest, BaseResponse, BaseTestResult
from sitecomber.apps.shared.utils import LinkParser, TitleParser, load_url

logger = logging.getLogger('django')


# class RequestHeader(BaseHeader):
#     parent = models.ForeignKey(
#         'results.PageRequest',
#         null=False,
#         on_delete=models.CASCADE
#     )


# class ResponseHeader(BaseHeader):
#     parent = models.ForeignKey(
#         'results.PageResponse',
#         null=False,
#         on_delete=models.CASCADE
#     )


class PageResponse(BaseMetaData, BaseResponse):
    """
    Represents a single request and response from the server
    """

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

    @property
    def time_elapsed_ms(self):
        if self.load_end_time and self.load_start_time:
            dt = self.load_end_time - self.load_start_time
            return int(round(dt.total_seconds() * 1000))
        return None

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

        try:
            r.response_headers = r.prepare_header_dict_for_db(dict(response.headers))
            r.save()
            return r
        except Exception as e:
            logger.error(u"Error saving response for URL %s: %s" % (response.url, e))
            logger.error(response.url)
            logger.error(response.status_code)

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
        self.method = BaseRequest.METHOD_GET if self.page_result.is_internal else BaseRequest.METHOD_HEAD
        self.request_url = self.page_result.url

        request_headers = {'user-agent': self.page_result.site_domain.site.get_user_agent()}
        self.request_headers = self.prepare_header_dict_for_db(request_headers)
        self.save()

        previous_item = None
        response, error_message = load_url(
            self.method,
            self.page_result.url,
            request_headers,
            self.page_result.site_domain.site.get_max_timeout_seconds()
        )
        if error_message or response.status_code != 200 and self.method == BaseRequest.METHOD_HEAD:
            logger.warn("HEAD Request was unsuccessful on %s, falling back to normal GET request." % (self.page_result.url))
            self.method = BaseRequest.METHOD_GET
            self.save()
            response, error_message = load_url(
                self.method,
                self.page_result.url,
                request_headers,
                self.page_result.site_domain.site.get_max_timeout_seconds()
            )

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

    title = models.CharField(max_length=1000, blank=True, null=True)
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

        if result.response and result.response.text_content:
            parser = TitleParser()
            parser.feed(result.response.text_content)
            self.title = parser.title

        self.last_load_time = timezone.now()
        self.save()

    @cached_property
    def latest_request(self):
        return self.pagerequest_set.order_by('-created').first()

    @cached_property
    def response_list(self):
        output = []
        if self.latest_request:
            response = self.latest_request.response
            while response:
                output.append(response)
                response = response.redirected_from

        output.reverse()
        return output

    @cached_property
    def test_results(self):
        return self.pagetestresult_set.all()

    @cached_property
    def successful_test_results(self):
        return self.test_results.filter(status=BaseTestResult.STATUS_SUCCESS)

    @cached_property
    def info_test_results(self):
        return self.test_results.filter(status=BaseTestResult.STATUS_INFO)

    @cached_property
    def warning_test_results(self):
        return self.test_results.filter(status=BaseTestResult.STATUS_WARNING)

    @cached_property
    def error_test_results(self):
        return self.test_results.filter(status=BaseTestResult.STATUS_ERROR)

    def save(self, *args, **kwargs):

        if not self.title:
            self.title = self.url

        super(PageResult, self).save(*args, **kwargs)

    def __str__(self):
        if self.title and self.title != self.url:
            return u'%s (%s)' % (self.title, Truncator(self.url).chars(80))
        return self.url

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
