from urllib.parse import urlparse

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property

from sitecomber.apps.shared.models import BaseMetaData, BaseURL

from sitecomber.apps.results.models import Page


class Site(BaseMetaData):

    owner = models.ForeignKey(
        get_user_model(),
        null=False,
        on_delete=models.PROTECT
    )
    title = models.CharField(max_length=255)

    # Crawling Settings
    recursive = models.BooleanField(default=True)
    override_user_agent = models.TextField(blank=True, null=True)
    override_max_redirects = models.IntegerField(blank=True, null=True)
    override_max_timeout_seconds = models.IntegerField(blank=True, null=True)

    @cached_property
    def canonical_domain(self):
        return self.sitedomain_set.filter(canonical=True).first()

    def get_user_agent(self):
        if self.override_user_agent:
            return self.override_user_agent
        return settings.DEFAULT_USER_AGENT

    def getmax_redirects(self):
        if self.override_max_redirects:
            return self.override_max_redirects
        return settings.DEFAULT_MAX_REDIRECTS

    def get_max_timeout_seconds(self):
        if self.override_max_timeout_seconds:
            return self.override_max_timeout_seconds
        return settings.DEFAULT_MAX_TIMEOUT_SECONDS

    def crawl(self):

        if not self.canonical_domain:
            raise ImproperlyConfigured(u"Site %s is missing a canonical domain. Please define at least one domain for this site." % (self))

        root_page, created = Page.objects.get_or_create(
            site=self,
            url=self.canonical_domain.url
        )

        root_page.load()

    def __str__(self):
        return self.title


class SiteDomain(BaseMetaData, BaseURL):

    project = models.ForeignKey(
        Site,
        null=False,
        on_delete=models.CASCADE
    )
    canonical = models.BooleanField(default=False)

    def save(self, *args, **kwargs):

        # Remove path from domain
        if self.url:
            self.url = urlparse(self.url)._replace(path='').geturl()

        # Make sure one and only one site domain in the project is canonical
        if self.canonical:
            self.project.sitedomain_set.all().exclude(pk=self.pk).filter(canonical=True).update(canonical=False)
        elif self.project.sitedomain_set.all().filter(canonical=True).count() == 0:
            self.canonical = True

        super(SiteDomain, self).save(*args, **kwargs)


class IgnoreURL(BaseMetaData, BaseURL):

    project = models.ForeignKey(
        Site,
        null=False,
        on_delete=models.CASCADE
    )


class IgnoreQueryParam(BaseMetaData):
    """
    If a url contains this query param, ignore it so that it doesn't get
    recognized as a different / unique URL
    """

    project = models.ForeignKey(
        Site,
        null=False,
        on_delete=models.CASCADE
    )
    param = models.CharField(max_length=255)
