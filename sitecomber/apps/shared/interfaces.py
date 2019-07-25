import logging
import traceback

# from django.core.exceptions import ImproperlyConfigured
logger = logging.getLogger('django')


class BaseSiteTest:
    """
    A base class for site and page tests
    """

    def __init__(self, site, settings):
        self.site = site
        self.settings = settings

    @property
    def class_path(self):
        return u'%s.%s' % (self.__class__.__module__, self.__class__.__name__)

    @property
    def description(self):
        html = self.get_description_html()
        if not html:
            return self.__doc__
        return html

    def page_parsed(self, page):
        try:
            self.on_page_parsed(page)
        except Exception as e:
            logger.error("Error applying test %s to page %s: %s %s" % (self, page, e, traceback.format_exc()))

    def sitemap_parsed(self, sitemap_item):
        try:
            self.on_sitemap_parsed(sitemap_item)
        except Exception as e:
            logger.error("Error applying test %s to sitemap %s: %s %s" % (self, sitemap_item, e, traceback.format_exc()))

    def get_description_html(self):
        return None

    def on_page_parsed(self, page):
        pass

    def on_sitemap_parsed(self, sitemap_item):
        pass
