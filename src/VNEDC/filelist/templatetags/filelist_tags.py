from django import template
import os

register = template.Library()

@register.filter
def basename(value):
    return os.path.basename(value)

@register.filter
def cut(value, delimiter):
    if delimiter in value:
        parts = value.rsplit(delimiter, 1)
        if len(parts) > 1:
            return parts[0]
    return ''
