from django import template
from ..consts import *

register = template.Library()

@register.filter
def css_class_by_type(type_name):
    return get_css_name(CHANGE_TYPES[type_name])
