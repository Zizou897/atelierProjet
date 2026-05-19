from django import template

register = template.Library()


@register.filter
def format_duration(visit):
    if not visit.start_date:
        return '—'
    end = visit.end_date or __import__('django.utils.timezone', fromlist=['now']).now()
    delta = end - visit.start_date
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes = remainder // 60
    return f"{hours}h{minutes:02d}"
