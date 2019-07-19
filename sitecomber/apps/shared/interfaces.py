import logging
import traceback

logger = logging.getLogger('django')


class BaseSiteTest:

    def __init__(self, site, settings):
        self.site = site
        self.settings = settings

    @property
    def class_path(self):
        return u'%s.%s' % (self.__class__.__module__, self.__class__.__name__)

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

    def on_page_parsed(self, page):
        pass

    def on_sitemap_parsed(self, sitemap_item):
        pass
