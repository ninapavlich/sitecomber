import logging
import importlib
import json
from urllib.parse import urlparse

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned
from django.urls import reverse
from django.utils.functional import cached_property

from usp.tree import sitemap_tree_for_homepage

from sitecomber.apps.shared.models import BaseMetaData, BaseURL, BaseTestResult, BasePath
from sitecomber.apps.shared.utils import get_domain, get_test_choices, log_memory
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

    max_page_results = models.IntegerField(blank=True, null=True,
                                           help_text="Limit the total number of pages crawled on a given site.")

    def get_absolute_url(self):
        return reverse('site-detail', args=[str(self.pk)])

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
        log_memory("before crawl")
        tests = self.tests
        log_memory("after tests")
        for domain in self.sitedomain_set.filter(should_crawl=True):
            domain.crawl(tests, load_batch_size)
        log_memory("after crawl")

    @cached_property
    def tests(self):
        return [item.class_instance for item in self.sitetestsetting_set.filter(active=True)]

    @cached_property
    def domains(self):
        return [item.url for item in self.sitedomain_set.all()]

    @cached_property
    def ignored_query_params(self):
        return [item.param for item in self.ignorequeryparam_set.all()]

    @cached_property
    def page_results(self):
        return PageResult.objects.filter(site_domain__site=self).defer('last_text_content')

    @cached_property
    def page_results_hierarchy(self):
        results = self.internal_page_results
        tree = {}
        for result in results:
            result_url_parsed = urlparse(result.url)
            result_url_parsed_split = [path for path in result_url_parsed.path.split('/') if path]

            child = tree
            last_piece = None
            last_child = None
            running_path = get_domain(result.url)
            for piece in result_url_parsed_split:
                last_piece = piece
                last_child = child
                running_path = '%s/%s' % (running_path, piece)
                if piece not in child:
                    child[piece] = {
                        'path': piece,
                        'page': None,
                        'page_url': None,
                        'full_path': running_path,
                        'children': {}
                    }
                child = child[piece]['children']
            if last_piece:
                last_child[last_piece]['page'] = result
                last_child[last_piece]['page_url'] = result.url

        return tree

    @cached_property
    def root_page_result(self):
        return self.page_results.filter(is_root=True).first()

    @cached_property
    def internal_page_results(self):
        return self.page_results.filter(is_internal=True)

    @cached_property
    def external_page_results(self):
        return self.page_results.filter(is_internal=False)

    @cached_property
    def uncrawled_page_results(self):
        return self.page_results.filter(last_load_start_time=None)

    @cached_property
    def has_fully_crawled_site(self):
        return self.uncrawled_page_results.count() == 0

    @cached_property
    def page_test_results(self):
        return PageTestResult.objects.filter(page__site_domain__site=self).select_related('page').defer('data', 'page__last_text_content')

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

    def get_test_results_for_test(self, test, status=None):
        results = self.page_test_results.filter(test=test)

        if status:
            results = results.filter(status=status)

        return results

    @cached_property
    def pages_with_errors(self):

        # Optimized version
        return list(set([page for page in PageTestResult.objects.filter(
            page__site_domain__site=self,
            page__is_internal=True,
            status=BaseTestResult.STATUS_ERROR
        ).only('page')]))

        # 2.5s SLOWER VERSION
        # return list(set([item.page for item in self.error_page_test_results if item.page.is_internal]))

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
        log_memory('---- a. Before creating root page')

        user_agent = self.site.get_user_agent()
        max_timeout = self.site.get_max_timeout_seconds()

        try:
            root_page, created = PageResult.objects.get_or_create(
                site_domain=self,
                url=self.url,
                defaults={'is_root': True}
            )
            root_page.load(user_agent, max_timeout)
            log_memory('---- b. After loading root page')
            for test in tests:
                test.page_parsed(root_page)
                # log_memory('-------- c. After running test %s' % (test))
        except MultipleObjectsReturned as e:
            logger.error("MultipleObjectsReturned when creating root page for site %s with url %s: %s" % (self, self.url, e))

        sitemap_ctr = 0
        page_ctr = 0
        log_memory('---- d. Before getting sitemap tree')
        tree = sitemap_tree_for_homepage(self.url)
        if hasattr(tree, 'sub_sitemaps'):
            for sitemap in tree.sub_sitemaps:
                sitemap_ctr += 1

                sitemap_item = self.handle_link(sitemap.url, None, True, True)
                sitemap_item.is_sitemap = True
                sitemap_item.save()

                for sitemap_item_url in sitemap.all_pages():
                    self.handle_link(sitemap_item_url.url, sitemap_item)
                    page_ctr += 1

                for test in tests:
                    test.sitemap_parsed(sitemap_item)

        log_memory('---- e. After getting sitemap tree')
        logger.debug("Found %s pages in %s sitemap(s)" % (page_ctr, sitemap_ctr))

    def crawl(self, tests, load_batch_size):

        log_memory("-- Starting domain crawl for %s" % (self))

        user_agent = self.site.get_user_agent()
        max_timeout = self.site.get_max_timeout_seconds()

        # First add the root page
        try:
            root_page, created = PageResult.objects.get_or_create(
                site_domain=self,
                url=self.url,
                defaults={'is_root': True}
            )
        except MultipleObjectsReturned as e:
            logger.error("MultipleObjectsReturned when creating root page for site %s with url %s: %s" % (self, self.url, e))

        # Now also add seed pages
        for seed_url in self.site.includeseed_set.all():
            if self.url in seed_url.url:
                self.handle_link(seed_url.url, None, True, True)

        if self.site.recursive:
            pages = PageResult.get_batch_to_load(self, root_page.pk, load_batch_size)

            logger.info("Found %s pages within the %s site, going to load a max of %s" % (len(pages), self, load_batch_size))
            log_memory("---- After retrieving pages")

            ctr = 0
            for page in pages:
                ctr += 1
                # log_memory("---- Before loading page %s" % (ctr))
                page.load(user_agent, max_timeout)
                # log_memory("---- After loading page %s" % (ctr))
                for test in tests:
                    test.page_parsed(page)
                    # log_memory("------ After applying test %s to page %s" % (test, ctr))
                page.render_synoposes()

        log_memory("-- After domain crawl for %s" % (self))

    def handle_link(self, url, source_page=None, is_internal=True, force_create=False):

        if not force_create:

            reached_page_result_max_for_site = False if not self.site.max_page_results else PageResult.objects.filter(site_domain__site=self.site).count() >= self.site.max_page_results
            if reached_page_result_max_for_site:
                logger.debug("Cannot create any new page results for site %s. Max of %s has been hit." % (self.site, self.site.max_page_results))
                return None

            ignore_paths = self.site.ignoreresult_set.all()
            for ignore_path in ignore_paths:
                if ignore_path.test(url):
                    logger.debug("Ignoring url %s based on ignore path %s" % (url, ignore_path))
                    return None

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
            return None

    @staticmethod
    def autocomplete_search_fields():
        return ("url__icontains", "site__title__icontains",)

    @classmethod
    def autocomplete_text(cls, item):
        return str(item)

    @classmethod
    def autocomplete_selected_text(cls, item):
        return str(item)


class IncludeSeed(BaseMetaData, BaseURL):
    """
    If a URL is not available through the homepage or sitemap, include this seed URL
    """
    site = models.ForeignKey(
        Site,
        null=False,
        on_delete=models.CASCADE
    )


class IgnoreResult(BaseMetaData, BasePath):

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

        if self.settings:
            try:
                settings_json = json.loads(self.settings)
            except ValueError:
                logger.error(u"Error validating test settings JSON: %s" % (self.settings))
        else:
            settings_json = {}

        class_ = self.class_model
        return class_(self.site, settings_json)

    @property
    def class_model(self):
        if not self.test:
            return None
        module_name, class_name = self.test.rsplit('.', 1)
        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)
        return class_

    @property
    def test_name(self):
        module_name, class_name = self.test.rsplit('.', 1)
        return class_name

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
