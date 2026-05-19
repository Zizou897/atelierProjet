from django import template

register = template.Library()


@register.filter
def full_name(customer):
    return f"{customer.first_name} {customer.last_name}".strip()
