from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin


class LinkParser(HTMLParser):

    canonical_domain = None
    alias_domains = []

    links = []
    mailto_links = []
    tel_links = []
    other_links = []
    internal_links = []
    external_links = []

    def __init__(self, canonical_domain, alias_domains):
        self.canonical_domain = canonical_domain
        alias_domains.append(canonical_domain)
        self.alias_domains = list(set(alias_domains))
        super().__init__()

    def reset(self):
        HTMLParser.reset(self)
        self.links = []
        self.mailto_links = []
        self.tel_links = []
        self.other_links = []
        self.internal_links = []
        self.external_links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attrs = dict(attrs)
            self.handle_link(attrs["href"])

    def handle_link(self, url):

        # Remove front end fragment
        url = urlparse(url)._replace(fragment='').geturl()

        self.links.append(url)

        if 'mailto:' in url.lower():
            self.mailto_links.append(url)

        elif 'tel:' in url.lower():
            self.tel_links.append(url)

        elif (':' in url.lower()) and ('http' not in url.lower()):
            self.other_links.append(url)

        else:
            if '//' not in url.lower():
                self.internal_links.append(urljoin(self.canonical_domain, url))
            else:

                is_internal = False

                url_domain = urlparse(url)._replace(path='', query='', fragment='').geturl()

                for domain in self.alias_domains:
                    if domain.lower() in url_domain.lower():
                        is_internal = True

                if is_internal:
                    self.internal_links.append(urljoin(self.canonical_domain, url))
                else:
                    self.external_links.append(url)
