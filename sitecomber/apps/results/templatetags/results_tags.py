import re
import logging

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

logger = logging.getLogger('django')


@register.simple_tag
def get_test_result_by_type(value, arg):
    return value.get_test_result_by_type(arg)


@register.filter(needs_autoescape=True)
@stringfilter
def highlight_spelling_errors(value, misspellings, autoescape=True):
    for word in misspellings:

        try:
            pattern = re.compile(word, re.IGNORECASE)
            value = pattern.sub(r"<span class='bg-danger text-light'>\g<0></span>", value)
        except Exception as e:
            logger.error("Error highlighting misspellings: %s" % (e))

    return mark_safe(value)


@register.simple_tag
def get_test_results_for_test(site, test, status=None):
    return site.get_test_results_for_test(test, status)


@register.simple_tag
def filter_page_test_results(page_test_results, test, status):

    output = [result for result in page_test_results if (result.test == test and result.status == status)]

    print("There are %s %s.%s results from %s" % (len(output), test, status, len(page_test_results)))

    return output
