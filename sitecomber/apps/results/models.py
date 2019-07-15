from django.db import models
from django.conf import settings
from django.utils import timezone

import requests

from sitecomber.apps.shared.models import BaseMetaData, BaseURL, BaseHeader, BaseRequest, BaseResponse


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
        r = cls(
            response_url=response.url,
            status_code=response.status_code,
            text_content=response.text,
            request=request,
            load_start_time=request.load_start_time,
            load_end_time=request.load_start_time + response.elapsed,
            redirected_from=redirected_from
        )

        r.save()
        r.create_response_headers(response.headers)
        return r


class PageRequest(BaseMetaData, BaseRequest):
    """
    Represents an entire chain of requests and responses until finally
    a non-redirecting response is given
    """
    request_header_model = RequestHeader

    page = models.ForeignKey(
        'results.Page',
        on_delete=models.CASCADE
    )

    status_code = models.CharField(max_length=255, blank=True, null=True)
    load_start_time = models.DateTimeField(blank=True, null=True)
    load_end_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return u'%s at %s' % (self.request_url, self.load_start_time)

    def load(self):
        self.load_start_time = timezone.now()
        self.method = BaseRequest.METHOD_GET
        self.request_url = self.page.url
        self.save()

        request_headers = {'user-agent': self.page.site.get_user_agent()}
        self.create_request_headers(request_headers)

        response = requests.get(self.page.url,
                                headers=request_headers,
                                timeout=self.page.site.get_max_timeout_seconds()
                                )

        self.load_end_time = timezone.now()
        self.status_code = response.status_code
        self.save()

        previous_item = None
        for item in response.history:
            previous_item = PageResponse.parse_response(self, previous_item, item)

        PageResponse.parse_response(self, previous_item, response)


class Page(BaseMetaData, BaseURL):

    site = models.ForeignKey(
        'config.Site',
        on_delete=models.CASCADE
    )

    def load(self):
        result = PageRequest(page=self)
        result.save()
        result.load()
