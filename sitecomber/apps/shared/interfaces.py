class BaseSiteTest:

    def __init__(self, site, settings):
        self.site = site
        self.settings = settings

    @property
    def class_path(self):
        return u'%s.%s' % (self.__class__.__module__, self.__class__.__name__)

    def on_page_parsed(self, page):
        # print("Page parsed on site!")
        pass

    def on_sitemap_parsed(self, page):
        # print("Sitemap parsed on site!")
        pass
