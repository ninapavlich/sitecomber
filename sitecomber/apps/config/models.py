import logging
import importlib
import json

from django.db import models
from django.db.models import F
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned
from django.utils.functional import cached_property

from usp.tree import sitemap_tree_for_homepage

from sitecomber.apps.shared.models import BaseMetaData, BaseURL, BaseTestResult
from sitecomber.apps.shared.utils import get_domain, get_test_choices
from sitecomber.apps.results.models import PageResult, PageTestResult


logger = logging.getLogger('django')


class Site(BaseMetaData):

    owner = models.ForeignKey(
        get_user_model(),
        null=False,
        on_delete=models.PROTECT
    )
    title = models.CharField(max_length=255)

    # Crawling Settings
    active = models.BooleanField(default=True)
    recursive = models.BooleanField(default=True)
    override_user_agent = models.TextField(blank=True, null=True)
    override_max_timeout_seconds = models.IntegerField(blank=True, null=True)

    def get_user_agent(self):
        if self.override_user_agent:
            return self.override_user_agent
        return settings.DEFAULT_USER_AGENT

    def get_max_timeout_seconds(self):
        if self.override_max_timeout_seconds:
            return self.override_max_timeout_seconds
        return settings.DEFAULT_MAX_TIMEOUT_SECONDS

    def parse_sitemap(self):
        tests = self.tests
        for domain in self.sitedomain_set.filter(should_crawl=True):
            domain.parse_sitemap(tests)

    def crawl(self, load_batch_size):
        tests = self.tests
        for domain in self.sitedomain_set.filter(should_crawl=True):
            domain.crawl(tests, load_batch_size)

    @cached_property
    def tests(self):
        return [item.class_instance for item in self.sitetestsetting_set.all()]

    @cached_property
    def domains(self):
        return [item.url for item in self.sitedomain_set.all()]

    @cached_property
    def ignored_query_params(self):
        return [item.param for item in self.ignorequeryparam_set.all()]

    @cached_property
    def page_results(self):
        return PageResult.objects.filter(site_domain__site=self)

    @cached_property
    def internal_page_results(self):
        return self.page_results.filter(is_internal=True)

    @cached_property
    def external_page_results(self):
        return self.page_results.filter(is_internal=False)

    @cached_property
    def uncrawled_page_results(self):
        return self.page_results.filter(last_load_time=None)

    @cached_property
    def has_fully_crawled_site(self):
        return self.uncrawled_page_results.count() == 0

    @cached_property
    def page_test_results(self):
        return PageTestResult.objects.filter(page__site_domain__site=self).select_related('page')

    @cached_property
    def successful_page_test_results(self):
        return self.page_test_results.filter(status=BaseTestResult.STATUS_SUCCESS)

    @cached_property
    def info_page_test_results(self):
        return self.page_test_results.filter(status=BaseTestResult.STATUS_INFO)

    @cached_property
    def warning_page_test_results(self):
        return self.page_test_results.filter(status=BaseTestResult.STATUS_WARNING)

    @cached_property
    def error_page_test_results(self):
        return self.page_test_results.filter(status=BaseTestResult.STATUS_ERROR)

    @cached_property
    def pages_with_errors(self):
        # TODO -- optimize
        return list(set([item.page for item in self.error_page_test_results]))

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

    def save(self, *args, **kwargs):

        # Remove path and query from domain
        if self.url:
            self.url = get_domain(self.url)

        # Don't allow alias to point to self
        if self.alias_of and self.alias_of == self:
            self.alias_of = None

        # Don't crawl domains that are simply aliases
        if self.alias_of:
            self.crawl = False

        super(SiteDomain, self).save(*args, **kwargs)

    def parse_sitemap(self, tests):

        try:
            root_page, created = PageResult.objects.get_or_create(
                site_domain=self,
                url=self.url,
                defaults={'is_root': True}
            )
            root_page.load()
            for test in tests:
                test.page_parsed(root_page)
        except MultipleObjectsReturned as e:
            logger.error("MultipleObjectsReturned when creating root page for site %s with url %s: %s" % (self, self.url, e))

        sitemap_ctr = 0
        page_ctr = 0
        tree = sitemap_tree_for_homepage(self.url)
        for sitemap in tree.sub_sitemaps:
            sitemap_ctr += 1
            sitemap_item = self.handle_link(sitemap.url)
            sitemap_item.is_sitemap = True
            sitemap_item.save()
            for sitemap_item_url in sitemap.all_pages():
                self.handle_link(sitemap_item_url.url, sitemap_item)
                page_ctr += 1

            for test in tests:
                test.sitemap_parsed(sitemap_item)

        logger.info("Found %s pages in %s sitemap(s)" % (page_ctr, sitemap_ctr))

    def crawl(self, tests, load_batch_size):

        try:
            root_page, created = PageResult.objects.get_or_create(
                site_domain=self,
                url=self.url,
                defaults={'is_root': True}
            )
        except MultipleObjectsReturned as e:
            logger.error("MultipleObjectsReturned when creating root page for site %s with url %s: %s" % (self, self.url, e))

        if self.site.recursive:

            pages = PageResult.objects\
                .filter(site_domain=self)\
                .exclude(pk=root_page.pk)\
                .order_by(F('last_load_time').desc(nulls_last=True)).reverse()

            logger.info("Found %s pages within the %s site, going to load a max of %s" % (pages.count(), self, load_batch_size))

            pages_to_load = pages[:load_batch_size]
            for page in pages_to_load:
                page.load()
                for test in tests:
                    test.page_parsed(page)

    def handle_link(self, url, source_page=None, is_internal=True):

        try:
            link_page, created = PageResult.objects.get_or_create(
                site_domain=self,
                url=url,
                defaults={'is_internal': is_internal}
            )
            if source_page:
                link_page.incoming_links.add(source_page)
                source_page.outgoing_links.add(link_page)
            return link_page

        except MultipleObjectsReturned as e:
            logger.error("MultipleObjectsReturned when creating page result for site %s with url %s: %s" % (self, self.url, e))

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

    def __str__(self):
        return self.param


class SiteTestSetting(BaseMetaData):

    site = models.ForeignKey(
        'config.Site',
        on_delete=models.CASCADE
    )
    test = models.CharField(max_length=255, choices=get_test_choices())
    active = models.BooleanField(default=True)
    settings = models.TextField(null=True, blank=True)

    @property
    def class_instance(self):
        if not self.test:
            return None
        module_name, class_name = self.test.rsplit('.', 1)
        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)

        if self.settings:
            try:
                settings_json = json.loads(self.settings)
            except ValueError:
                logger.error(u"Error validating test settings JSON: %s" % (self.settings))
        else:
            settings_json = {}

        return class_(self.site, settings_json)

    def save(self, *args, **kwargs):

        # Validate settings JSON
        if self.settings:
            try:
                settings_json = json.loads(self.settings)
                self.settings = json.dumps(settings_json, sort_keys=True, indent=2)
            except ValueError:
                logger.error(u"Error validating test settings JSON: %s" % (self.settings))

        super(SiteTestSetting, self).save(*args, **kwargs)

    def __str__(self):
        return u'%s for %s' % (self.test, self.site)
