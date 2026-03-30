from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.workshop_dashboard_view, name="workshop_dashboard"),
    path("passages/", views.workshop_visit_list_view, name="workshop_visit_list"),
    path("techniciens/", views.technician_list_view, name="workshop_technician_list"),
    path("techniciens/nouveau/", views.technician_create_view, name="workshop_technician_create"),
]
