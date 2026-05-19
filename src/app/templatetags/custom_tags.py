from django import template

register = template.Library()


@register.filter
def default_if_none(value, default='—'):
    return value if value is not None else default
