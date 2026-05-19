from django import template

register = template.Library()


@register.filter
def has_role(user, role_name: str) -> bool:
    return user.groups.filter(name=role_name).exists()
