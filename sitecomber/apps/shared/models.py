from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse

from encrypted_model_fields.fields import EncryptedCharField

from .utils import get_test_choices


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


class BaseAuthenticationCredentials(models.Model):
    # TODO

    AUTH_NONE = 'none'
    AUTH_BASIC = 'basic_auth'
    AUTHENTICATION_TYPES = (
        (AUTH_NONE, 'None'),
        (AUTH_BASIC, 'Basic Auth'),
    )
    authentication_type = models.CharField(max_length=16, choices=AUTHENTICATION_TYPES,
                                           default=AUTH_NONE)

    authentication_data = EncryptedCharField(max_length=10000, null=True, blank=True)

    def __str__(self):
        return u'%s %s' % (self.pk, self.authentication_type)

    class Meta:
        abstract = True


class BaseURL(BaseAuthenticationCredentials):

    title = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(max_length=2000)

    def __str__(self):
        return self.url

    class Meta:
        abstract = True


class BaseHeader(models.Model):
    """
    If header is used with a request or response, make sure to define
    a field called 'parent' which is an FK to the corresponding request or
    response
    """
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True


def create_headers(parent_instance, header_model, dict):
    for key, val in dict.items():
        obj, created = header_model.objects.get_or_create(
            parent=parent_instance,
            key=key,
            defaults={'value': val},
        )


class BaseRequest(models.Model):

    request_url = models.URLField()

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

    def create_request_headers(self, dict):
        if not self.request_header_model:
            raise ImproperlyConfigured(u"%s doesn't define its corresponding self.request_header_model" % (self._meta.model_name))

        create_headers(self, self.request_header_model, dict)

    def get_request_header_by_key(self, key):
        return self.request_header_model.objects.filter(parent=self, key=key).first()

    class Meta:
        abstract = True


class BaseResponse(models.Model):

    response_url = models.URLField()
    status_code = models.IntegerField(blank=True, null=True)
    content_type = models.CharField(max_length=255, blank=True, null=True)
    content_length = models.IntegerField(blank=True, null=True)
    http_version = models.CharField(max_length=255, blank=True, null=True)
    remote_address = models.CharField(max_length=255, blank=True, null=True)

    def create_response_headers(self, dict):
        if not self.response_header_model:
            raise ImproperlyConfigured(u"%s doesn't define its corresponding self.response_header_model" % (self._meta.model_name))

        create_headers(self, self.response_header_model, dict)

    def get_response_header_by_key(self, key):
        return self.response_header_model.objects.filter(parent=self, key=key).first()

    class Meta:
        abstract = True


class BaseTestResult(models.Model):

    test = models.CharField(max_length=255, choices=get_test_choices())
    data = models.TextField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)

    STATUS_INFO = 'info'
    STATUS_WARNING = 'warning'
    STATUS_SUCCESS = 'success'
    STATUS_ERROR = 'error'
    STATUSES = (
        (STATUS_INFO, 'Info'),
        (STATUS_WARNING, 'Warning'),
        (STATUS_SUCCESS, 'Success'),
        (STATUS_ERROR, 'Error'),
    )
    status = models.CharField(max_length=16, choices=STATUSES, default=STATUS_INFO)

    def __str__(self):
        return u'%s. %s on %s' % (self.pk, self.status, self.test)

    class Meta:
        abstract = True
