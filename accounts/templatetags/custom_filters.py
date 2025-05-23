from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def split(value, arg):
    """Split a string by the given argument"""
    return value.split(arg) 