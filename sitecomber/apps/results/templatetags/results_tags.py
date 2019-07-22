from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def get_test_result_by_type(value, arg):
    return value.get_test_result_by_type(arg)


@register.filter(needs_autoescape=True)
@stringfilter
def highlight_spelling_errors(value, misspellings, autoescape=True):
    for word in misspellings:
        value = value.replace(word, "<span class='bg-danger text-light'>%s</span>" % word)
        value = value.replace(word.capitalize(), "<span class='bg-danger text-light'>%s</span>" % word)
    return mark_safe(value)
