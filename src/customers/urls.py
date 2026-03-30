from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.customer_dashboard_view, name="customer_dashboard"),
    path("", views.customer_list_view, name="customer_list"),
    path("new/", views.customer_create_view, name="customer_create"),
    path("<int:customer_id>/", views.customer_detail_view, name="customer_detail"),
    path("<int:customer_id>/edit/", views.customer_update_view, name="customer_update"),
]
