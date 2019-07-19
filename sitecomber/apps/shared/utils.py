import logging
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin, parse_qs, urlencode

import requests

from .interfaces import BaseSiteTest

logger = logging.getLogger('django')


def get_domain(url):
    return urlparse(url)._replace(path='', query='', fragment='').geturl()


def standardize_url(url, ignored_query_params):
    # First removed any frontend fragments:
    url = urlparse(url)._replace(fragment='').geturl()

    # If path = "/" then remove it
    if urlparse(url).path == '/':
        url = urlparse(url)._replace(path='').geturl()

    # Next remove unwanted QS
    parsed_url = urlparse(url)
    parsed_qs = parse_qs(parsed_url.query)

    for param in ignored_query_params:
        if param in parsed_qs:
            del(parsed_qs[param])

    return urlparse(url)._replace(query=urlencode(parsed_qs, True)).geturl()


class LinkParser(HTMLParser):

    canonical_domain = None
    alias_domains = []
    ignored_query_params = []

    links = []
    mailto_links = []
    tel_links = []
    other_links = []
    internal_links = []
    external_links = []

    def __init__(self, canonical_domain, alias_domains, ignored_query_params):
        self.canonical_domain = canonical_domain
        alias_domains.append(canonical_domain)
        self.alias_domains = list(set(alias_domains))
        self.ignored_query_params = ignored_query_params
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

        # standardize URL:
        url = standardize_url(url, self.ignored_query_params)

        self.links.append(url)

        if 'mailto:' in url.lower():
            self.mailto_links.append(url)

        elif 'tel:' in url.lower():
            self.tel_links.append(url)

        elif (':' in url.lower()) and ('http' not in url.lower()):
            self.other_links.append(url)

        else:
            if '//' not in url.lower():
                self.handle_internal_link(url)
            else:

                is_internal = False

                url_domain = get_domain(url)

                for domain in self.alias_domains:
                    if domain.lower() in url_domain.lower():
                        is_internal = True

                if is_internal:
                    self.handle_internal_link(url)
                else:
                    self.external_links.append(url)

    def handle_internal_link(self, url):
        self.internal_links.append(urljoin(self.canonical_domain, url))


class TitleParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.match = False
        self.title = ''

    def handle_starttag(self, tag, attributes):
        self.match = True if tag == 'title' else False

    def handle_data(self, data):
        if self.match:
            self.title = data
            self.match = False


def class_to_path(cls):
    return u'%s.%s' % (cls.__module__, cls.__name__)


def get_test_choices():
    """
    Returns a list of all items that extend the BaseSiteTest base class
    """
    subclasses = BaseSiteTest.__subclasses__()
    if len(subclasses) == 0:
        logger.warn("No classes found that extend BaseSiteTest. Please verify that you have installed some tests.")

    return [(class_to_path(cls), cls.__name__) for cls in subclasses]


def load_url(method, url, request_headers, timeout):
    response = None
    error_message = None
    try:
        response = requests.request(
            method,
            url,
            headers=request_headers,
            timeout=timeout
        )
    except requests.exceptions.ConnectionError as e:
        error_message = "ERROR: Connection Error when trying to load %s: %s" % (url, e)
    except requests.exceptions.Timeout as e:
        error_message = "ERROR: Timeout when trying to load %s: %s" % (url, e)
    except requests.exceptions.RequestException as e:
        error_message = "ERROR: Request Exception when trying to load %s: %s" % (url, e)
    except requests.exceptions.TooManyRedirects as e:
        error_message = "ERROR: Too many redirects when trying to load %s: %s" % (url, e)

    return response, error_message
