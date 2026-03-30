from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.vehicle_dashboard_view, name="vehicle_dashboard"),
    path("", views.vehicle_list_view, name="vehicle_list"),
    path("create/", views.vehicle_create_view, name="vehicle_create"),
    path("<int:vehicle_id>/", views.vehicle_detail_view, name="vehicle_detail"),
    path("<int:vehicle_id>/edit/", views.vehicle_update_view, name="vehicle_update"),
    path(
        "<int:vehicle_id>/passages/new/",
        views.vehicle_visit_create_view,
        name="vehicle_visit_create",
    ),
    path(
        "<int:vehicle_id>/passages/<int:visit_id>/edit/",
        views.vehicle_visit_update_view,
        name="vehicle_visit_update",
    ),
]
