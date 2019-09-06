import logging
import json
from fnmatch import fnmatch

from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property

# from encrypted_model_fields.fields import EncryptedCharField

from .utils import get_test_choices

logger = logging.getLogger('django')


class BaseMetaData(models.Model):
    """A base class to manage metadata shared between models
    """

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def get_edit_url(self):
        return reverse("admin:%s_%s_change" % (
            self._meta.app_label,
            self._meta.model_name
        ), args=(self.pk,))

    class Meta:
        abstract = True


# class BaseAuthenticationCredentials(models.Model):
#     # TODO
#
#     AUTH_NONE = 'none'
#     AUTH_BASIC = 'basic_auth'
#     AUTHENTICATION_TYPES = (
#         (AUTH_NONE, 'None'),
#         (AUTH_BASIC, 'Basic Auth'),
#     )
#     authentication_type = models.CharField(max_length=16, choices=AUTHENTICATION_TYPES,
#                                            default=AUTH_NONE)
#
#     authentication_data = EncryptedCharField(max_length=10000, null=True, blank=True)
#
#     def __str__(self):
#         return u'%s %s' % (self.pk, self.authentication_type)
#
#     class Meta:
#         abstract = True


class BaseURL(models.Model):

    title = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(max_length=2000)

    def __str__(self):
        return self.url

    class Meta:
        abstract = True


class BasePath(models.Model):

    title = models.CharField(max_length=255, blank=True, null=True)
    path = models.CharField(max_length=2000, help_text='Match either a fully qualified URL or paths using Unix shell-style wildcards, e.g. */files/*.txt')

    def __str__(self):
        return self.path

    def test(self, test_url):
        return fnmatch(test_url, self.path)

    class Meta:
        abstract = True


class BaseHeaders(models.Model):

    def validate_header_string_for_db(self, raw_headers):
        try:
            headers_json = json.loads(raw_headers)
            return json.dumps(headers_json, sort_keys=True, indent=2)
        except ValueError:
            logger.error(u"Error validating response headers JSON: %s" % (self.response_headers))

        return raw_headers

    def prepare_header_dict_for_db(self, header_dict):
        try:
            return json.dumps(header_dict, sort_keys=True, indent=2)
        except ValueError:
            logger.error(u"Error creating headers JSON from: %s" % (header_dict))
            return None

    def get_header_by_key(self, raw_headers, key):
        try:
            headers_json = json.loads(raw_headers)
            return headers_json.get(key)
        except ValueError:
            logger.error(u"Error parsing headers JSON: %s" % (raw_headers))
        return None

    def get_header_json(self, raw_headers):
        try:
            return json.loads(raw_headers)
        except ValueError:
            logger.error(u"Error parsing headers JSON: %s" % (raw_headers))
        return None

    class Meta:
        abstract = True


class BaseRequest(BaseHeaders):

    request_url = models.URLField(max_length=2000)

    METHOD_GET = 'GET'
    METHOD_HEAD = 'HEAD'
    METHOD_POST = 'POST'
    METHOD_PUT = 'PUT'
    METHOD_DELETE = 'DELETE'
    METHOD_CONNECT = 'CONNECT'
    METHOD_OPTIONS = 'OPTIONS'
    METHOD_TRACE = 'TRACE'
    METHOD_PATCH = 'PATCH'
    REQUEST_METHODS = (
        (METHOD_GET, METHOD_GET),
        (METHOD_HEAD, METHOD_HEAD),
        (METHOD_POST, METHOD_POST),
        (METHOD_PUT, METHOD_PUT),
        (METHOD_DELETE, METHOD_DELETE),
        (METHOD_CONNECT, METHOD_CONNECT),
        (METHOD_OPTIONS, METHOD_OPTIONS),
        (METHOD_TRACE, METHOD_TRACE),
        (METHOD_PATCH, METHOD_PATCH),

    )
    method = models.CharField(max_length=255, choices=REQUEST_METHODS,
                              blank=True, null=True)

    request_headers = models.TextField(blank=True, null=True)

    @cached_property
    def request_header_json(self):
        if self.request_headers:
            return self.get_header_json(self.request_headers)

    def save(self, *args, **kwargs):

        # Validate JSON
        if self.request_headers:
            self.request_headers = self.validate_header_string_for_db(self.request_headers)

        super(BaseRequest, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class BaseResponse(BaseHeaders):

    response_url = models.URLField(max_length=2000)
    status_code = models.IntegerField(blank=True, null=True)
    content_type = models.CharField(max_length=255, blank=True, null=True)
    content_length = models.IntegerField(blank=True, null=True)
    http_version = models.CharField(max_length=255, blank=True, null=True)
    remote_address = models.CharField(max_length=255, blank=True, null=True)

    response_headers = models.TextField(blank=True, null=True)

    @cached_property
    def response_header_json(self):
        if self.response_headers:
            return self.get_header_json(self.response_headers)

    def save(self, *args, **kwargs):

        # Validate JSON
        if self.response_headers:
            self.response_headers = self.validate_header_string_for_db(self.response_headers)

        super(BaseResponse, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class TruncatingCharField(models.CharField):

    def get_prep_value(self, value):
        value = super(TruncatingCharField, self).get_prep_value(value)
        if value:
            return value[:self.max_length]
        return value


class BaseTestResult(models.Model):

    test = models.CharField(max_length=255, choices=get_test_choices())
    data = models.TextField(blank=True, null=True)
    message = TruncatingCharField(blank=True, null=True, max_length=2000)

    STATUS_NONE = 'none'
    STATUS_INFO = 'info'
    STATUS_WARNING = 'warning'
    STATUS_SUCCESS = 'success'
    STATUS_ERROR = 'error'
    STATUSES = (
        (STATUS_NONE, 'None'),
        (STATUS_INFO, 'Info'),
        (STATUS_WARNING, 'Warning'),
        (STATUS_SUCCESS, 'Success'),
        (STATUS_ERROR, 'Error'),
    )
    status = models.CharField(max_length=16, choices=STATUSES, default=STATUS_INFO)

    @cached_property
    def data_json(self):
        if self.data:
            try:
                return json.loads(self.data)
            except ValueError:
                logger.error(u"Error parsing data JSON: %s" % (self.data))
        return {}

    @cached_property
    def success(self):
        return self.status == BaseTestResult.STATUS_SUCCESS

    @cached_property
    def error(self):
        return self.status == BaseTestResult.STATUS_ERROR

    @cached_property
    def warning(self):
        return self.status == BaseTestResult.STATUS_WARNING

    @cached_property
    def info(self):
        return self.status == BaseTestResult.STATUS_INFO

    @property
    def test_title(self):
        return (self.test.split('.')[-1])

    @property
    def bootstrap_class(self):
        if self.status == 'error':
            return 'danger'
        return self.status

    def __str__(self):
        return u'%s. %s on %s' % (self.pk, self.status, self.test)

    class Meta:
        abstract = True
