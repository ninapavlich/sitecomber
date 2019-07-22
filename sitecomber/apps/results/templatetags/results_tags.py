from django import template

register = template.Library()


@register.simple_tag
def get_test_result_by_type(value, arg):
    return value.get_test_result_by_type(arg)
