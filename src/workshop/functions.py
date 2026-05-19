from django.db.models import QuerySet
from .models import WorkshopVisit, Technician


def get_active_visits() -> QuerySet:
    return WorkshopVisit.objects.filter(end_date__isnull=True).select_related('vehicle', 'technician')


def get_available_technicians() -> QuerySet:
    return Technician.objects.filter(publish=True) if hasattr(Technician, 'publish') else Technician.objects.all()
