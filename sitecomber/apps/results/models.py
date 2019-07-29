import logging
from urllib.parse import urlparse

from django.conf import settings
from django.db import models
from django.db.models import F
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.text import Truncator


from sitecomber.apps.shared.models import BaseMetaData, BaseURL, BaseRequest, BaseResponse, BaseTestResult
from sitecomber.apps.shared.utils import LinkParser, TitleParser, load_url


logger = logging.getLogger('django')


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

    @property
    def enumerated_source(self):
        if self.text_content:
            try:
                enumerated_source_list = self.text_content.split("\n")
                counter = 0
                source = u""
                for line in enumerated_source_list:
                    new_line = (u"%s: %s" % (counter, line))
                    source += (u"%s\n" % (new_line))
                    counter += 1
                return source
            except Exception as e:
                return u"Error enumerating source: %s" % (e)

    @property
    def archive_filename(self):
        parsed = urlparse(self.response_url)
        path = parsed.path[1:]
        if path == "":
            path = "index"
        return '%s.%s' % (path, self.archive_filetype)

    @property
    def archive_filetype(self):
        if not self.content_type:
            return 'txt'

        try:
            return self.content_type.split(";")[0].split("/")[1].split("+")[0]
        except Exception as e:
            logger.error(u"Error parsing content type from %s: %s" % (self.content_type, e))

        return 'txt'

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
            status_code=-1,
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

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return u'%s at %s' % (self.request_url, self.load_start_time)

    def load(self, user_agent, max_timeout):
        self.load_start_time = timezone.now()
        self.method = BaseRequest.METHOD_GET if self.page_result.is_internal else BaseRequest.METHOD_HEAD
        self.request_url = self.page_result.url

        request_headers = {'user-agent': user_agent}
        self.request_headers = self.prepare_header_dict_for_db(request_headers)
        self.save()

        previous_item = None
        response, error_message = load_url(
            self.method,
            self.page_result.url,
            request_headers,
            max_timeout
        )
        if error_message or response.status_code != 200 and self.method == BaseRequest.METHOD_HEAD:
            logger.warn("HEAD Request was unsuccessful on %s, falling back to normal GET request." % (self.page_result.url))
            self.method = BaseRequest.METHOD_GET
            self.save()
            response, error_message = load_url(
                self.method,
                self.page_result.url,
                request_headers,
                max_timeout
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
    last_load_start_time = models.DateTimeField(blank=True, null=True)
    last_load_end_time = models.DateTimeField(blank=True, null=True)
    last_status_code = models.IntegerField(blank=True, null=True)
    last_content_type = models.CharField(max_length=255, blank=True, null=True)
    last_content_length = models.IntegerField(blank=True, null=True)
    last_text_content = models.TextField(blank=True, null=True)

    error_synopsis = models.TextField(blank=True, null=True)
    warning_synoposis = models.TextField(blank=True, null=True)

    load_start_time = models.DateTimeField(blank=True, null=True)
    load_end_time = models.DateTimeField(blank=True, null=True)

    incoming_links = models.ManyToManyField('self', symmetrical=False, related_name="page_incoming_links",)
    outgoing_links = models.ManyToManyField('self', symmetrical=False, related_name="page_outgoing_links",)

    is_sitemap = models.BooleanField(default=False)
    is_root = models.BooleanField(default=False)
    is_internal = models.BooleanField(default=True)

    @classmethod
    def _raw_get_batch_to_load(cls, site_domain, rook_pk, start_index, end_index):
        return cls.objects\
            .filter(site_domain=site_domain)\
            .exclude(pk=rook_pk)\
            .order_by(F('last_load_start_time').desc(nulls_last=True)).reverse()[start_index:end_index]

    @classmethod
    def get_batch_to_load(cls, site_domain, rook_pk, load_batch_size):

        # This version is very memory intensive if a queryset is very large:
        # pages = cls.objects\
        #     .filter(site_domain=self)\
        #     .exclude(pk=root_page.pk)\
        #     .order_by(F('last_load_start_time').desc(nulls_last=True)).reverse()

        # ctr = 0
        # for page in pages:
        #     log_memory("---- Before loading page %s" % (ctr))
        #     if ctr > load_batch_size:
        #         break
        #     if page.should_load():
        #         output.append(page)
        #         ctr += 1

        # This version handles pagination to load as little as possible:
        output = []
        ctr = 0
        batch_increment = 0
        page_size = 100

        while ctr < load_batch_size:
            next_batch = cls._raw_get_batch_to_load(site_domain, rook_pk, batch_increment, batch_increment + page_size)

            for page in next_batch:

                if ctr >= load_batch_size:
                    break
                if page.should_load():
                    output.append(page)
                    ctr += 1

            # If we dont have any more items in the list, then we are done here.
            if len(next_batch) < load_batch_size:
                ctr = load_batch_size
            else:
                batch_increment += page_size

        return output

    def should_load(self):
        do_load = False
        if not self.last_load_start_time:
            do_load = True
        else:
            time_since_last_load = timezone.now() - self.last_load_start_time
            if self.is_internal:
                logger.debug(u"Time since last load: %s min is %s " % (time_since_last_load.total_seconds(), settings.MIN_SECONDS_BETWEEN_INTERNAL_PAGE_CRAWL))
                do_load = (time_since_last_load.total_seconds() > settings.MIN_SECONDS_BETWEEN_INTERNAL_PAGE_CRAWL)
            else:
                logger.debug(u"Time since last load: %s min is %s " % (time_since_last_load.total_seconds(), settings.MIN_SECONDS_BETWEEN_EXTERNAL_PAGE_CRAWL))
                do_load = (time_since_last_load.total_seconds() > settings.MIN_SECONDS_BETWEEN_EXTERNAL_PAGE_CRAWL)

        logger.debug(u"Should load %s? %s" % (self, do_load))
        return do_load

    def load(self, user_agent, max_timeout):
        logger.info(u"Loading %s" % (self))

        # First clean old records
        old_records = PageRequest.objects.filter(page_result=self).exclude(retain=True).order_by('-created')
        for old_record in old_records[settings.DEFAULT_MAINTAIN_PREVIOUS_RECORD_COUNT:]:
            old_record.delete()

        result = PageRequest(page_result=self)
        result.save()
        result.load(user_agent, max_timeout)

        if result.response:
            if result.response.text_content:
                parser = TitleParser()
                parser.feed(result.response.text_content)
                self.title = parser.title if parser.title else self.url
                self.last_text_content = result.response.text_content

            self.last_load_start_time = result.response.load_start_time
            self.last_load_end_time = result.response.load_end_time
            self.last_status_code = result.response.status_code
            self.last_content_type = result.response.content_type
            self.last_content_length = result.response.content_length
        else:
            self.last_load_start_time = self.last_load_end_time = timezone.now()
            self.last_status_code = None
            self.last_content_type = None
            self.last_content_length = None

        self.save()

    def render_synoposes(self):
        self.error_synopsis = render_to_string('results/partials/pagresult__error_synopsis.html', {'object': self})
        self.warning_synoposis = render_to_string('results/partials/pagresult__warning_synopsis.html', {'object': self})
        self.save()

    @property
    def last_time_elapsed_ms(self):
        if self.last_load_end_time and self.last_load_start_time:
            dt = self.last_load_end_time - self.last_load_start_time
            return int(round(dt.total_seconds() * 1000))
        return None

    @cached_property
    def latest_request(self):
        return self.pagerequest_set.select_related('response').order_by('-created').first()

    @cached_property
    def latest_response(self):
        for request in self.pagerequest_set.all():
            if request.response:
                return request.response
        return None

    @cached_property
    def incoming_links_with_prefetch(self):
        return self.incoming_links.all().prefetch_related('site_domain').prefetch_related('site_domain__site').prefetch_related('pagetestresult_set').prefetch_related('pagerequest_set').prefetch_related('pagerequest_set__response')

    @cached_property
    def outgoing_links_with_prefetch(self):
        return self.outgoing_links.all().prefetch_related('site_domain').prefetch_related('site_domain__site').prefetch_related('pagetestresult_set').prefetch_related('pagerequest_set').prefetch_related('pagerequest_set__response')

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
        # For some reason this is more db efficient than filtering
        return [test for test in self.pagetestresult_set.all() if test.status == BaseTestResult.STATUS_SUCCESS]
        # return self.pagetestresult_set.all().filter(status=BaseTestResult.STATUS_SUCCESS)

    @cached_property
    def info_test_results(self):
        # For some reason this is more db efficient than filtering
        return [test for test in self.pagetestresult_set.all() if test.status == BaseTestResult.STATUS_INFO]
        # return self.pagetestresult_set.all().filter(status=BaseTestResult.STATUS_INFO)

    @cached_property
    def warning_test_results(self):
        # For some reason this is more db efficient than filtering
        return [test for test in self.pagetestresult_set.all() if test.status == BaseTestResult.STATUS_WARNING]
        # return self.pagetestresult_set.all().filter(status=BaseTestResult.STATUS_WARNING)

    @cached_property
    def error_test_results(self):
        # For some reason this is more db efficient than filtering
        return [test for test in self.pagetestresult_set.all() if test.status == BaseTestResult.STATUS_ERROR]
        # return self.pagetestresult_set.all().filter(status=BaseTestResult.STATUS_ERROR)

    def get_test_result_by_type(self, test_type):
        # For some reason this is more db efficient than filtering
        for test in self.pagetestresult_set.all():
            if test.test == test_type:
                return test
        # return self.pagetestresult_set.all().filter(test=test_type).first()

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
