from django.contrib import admin

from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("registration_number", "make", "model", "customer", "owner_name", "mileage", "updated_at")
    search_fields = (
        "registration_number",
        "vin",
        "make",
        "model",
        "owner_name",
        "customer__first_name",
        "customer__last_name",
        "customer__company_name",
    )
    list_filter = ("fuel_type", "transmission")
