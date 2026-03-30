from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def cfa_thousands(value):
    if value in (None, ""):
        return "-"

    try:
        amount = int(Decimal(str(value)))
    except (InvalidOperation, ValueError, TypeError):
        return "-"

    return f"{amount:,}".replace(",", ".")
