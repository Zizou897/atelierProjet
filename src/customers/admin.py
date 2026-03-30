from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("display_name", "customer_type", "email", "phone", "city", "is_active")
    search_fields = ("first_name", "last_name", "company_name", "email", "phone", "city")
    list_filter = ("customer_type", "is_active", "city")
