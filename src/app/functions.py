from customers.models import Customer
from vehicles.models import Vehicle
from workshop.models import WorkshopVisit


def get_dashboard_stats() -> dict:
    return {
        'total_customers': Customer.objects.count(),
        'total_vehicles': Vehicle.objects.count(),
        'active_visits': WorkshopVisit.objects.filter(end_date__isnull=True).count(),
    }
