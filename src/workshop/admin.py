from django.contrib import admin

from .models import Maintenance, Technician, WorkshopVisit


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "opened_on", "status")
    search_fields = ("vehicle__registration_number",)
    list_filter = ("status", "opened_on")


@admin.register(WorkshopVisit)
class WorkshopVisitAdmin(admin.ModelAdmin):
    list_display = (
        "vehicle",
        "service",
        "maintenance",
        "visit_date",
        "start_date",
        "end_date",
        "status",
        "technician_name",
        "actual_cost",
    )
    search_fields = ("vehicle__registration_number", "service", "concern", "technician_name")
    list_filter = ("service", "status", "visit_date", "maintenance")


@admin.register(Technician)
class TechnicianAdmin(admin.ModelAdmin):
    list_display = ("full_name", "position", "atelier", "identification_number", "contact")
    search_fields = ("first_name", "last_name", "position", "identification_number", "atelier")
    list_filter = ("atelier", "position")
