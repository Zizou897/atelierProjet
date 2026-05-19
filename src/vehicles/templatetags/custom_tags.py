from django import template

register = template.Library()


@register.filter
def vehicle_label(vehicle):
    return f"{vehicle.brand} {vehicle.model} ({vehicle.year})"
