from django.db.models import QuerySet
from .models import Customer


def search_customers(query: str) -> QuerySet:
    if not query:
        return Customer.objects.all()
    return Customer.objects.filter(
        __import__('django.db.models', fromlist=['Q']).Q(first_name__icontains=query) |
        __import__('django.db.models', fromlist=['Q']).Q(last_name__icontains=query) |
        __import__('django.db.models', fromlist=['Q']).Q(email__icontains=query)
    )
