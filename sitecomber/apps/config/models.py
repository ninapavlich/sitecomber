import logging
from urllib.parse import urlparse

from django.db import models
from django.db.models import F
from django.conf import settings
from django.contrib.auth import get_user_model

from sitecomber.apps.shared.models import BaseMetaData, BaseURL

from sitecomber.apps.results.models import PageResult

logger = logging.getLogger('django')


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

    def crawl(self, urls_to_load):
        for domain in self.sitedomain_set.filter(should_crawl=True):
            domain.crawl(urls_to_load)

    @property
    def domains(self):
        return [item.url for item in self.sitedomain_set.all()]

    def __str__(self):
        return self.title


class SiteDomain(BaseMetaData, BaseURL):

    site = models.ForeignKey(
        Site,
        null=False,
        on_delete=models.CASCADE
    )
    alias_of = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    should_crawl = models.BooleanField(default=True)

    override_sitemap = models.CharField(max_length=255, blank=True, null=True, help_text='Name of sitemap file relative to the root, e.g. sitemap.xml')

    def get_sitemap(self):
        if self.override_sitemap:
            return self.override_sitemap
        return settings.DEFAULT_SITEMAP_URL

    def save(self, *args, **kwargs):

        # Remove path and query from domain
        if self.url:
            self.url = urlparse(self.url)._replace(path='', query='', fragment='').geturl()

        # Don't allow alias to point to self
        if self.alias_of and self.alias_of == self:
            self.alias_of = None

        # Don't crawl domains that are simply aliases
        if self.alias_of:
            self.crawl = False

        super(SiteDomain, self).save(*args, **kwargs)

    def crawl(self, urls_to_load):

        root_page, created = PageResult.objects.get_or_create(
            site_domain=self,
            url=self.url
        )
        root_page.load()

        # sitemap_page, created = PageResult.objects.get_or_create(
        #     site_domain=self,
        #     url=urlparse(self.url)._replace(path=self.get_sitemap()).geturl()
        # )
        # sitemap_page.load()

        # TODO - also limit items so that recently parsed URLs don't get re-parsed
        pages = PageResult.objects\
            .filter(site_domain=self)\
            .exclude(pk=root_page.pk)\
            .order_by(F('last_load_time').desc(nulls_last=True)).reverse()

        logger.info("Found %s pages within the %s site" % (pages.count(), self))

        pages_to_load = pages[:urls_to_load]
        for page in pages_to_load:
            page.load()

    @staticmethod
    def autocomplete_search_fields():
        return ("url__icontains", "site__title__icontains",)

    @classmethod
    def autocomplete_text(cls, item):
        return str(item)

    @classmethod
    def autocomplete_selected_text(cls, item):
        return str(item)


class IgnoreURL(BaseMetaData, BaseURL):

    site = models.ForeignKey(
        Site,
        null=False,
        on_delete=models.CASCADE
    )


class IgnoreQueryParam(BaseMetaData):
    """
    If a url contains this query param, ignore it so that it doesn't get
    recognized as a different / unique URL
    """

    site = models.ForeignKey(
        Site,
        null=False,
        on_delete=models.CASCADE
    )
    param = models.CharField(max_length=255)
