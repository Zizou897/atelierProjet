from django.db.models import QuerySet
from .models import Vehicle


def get_vehicles_for_customer(customer_id: int) -> QuerySet:
    return Vehicle.objects.filter(customer_id=customer_id)
