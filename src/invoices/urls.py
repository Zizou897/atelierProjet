from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.invoice_dashboard, name='invoice_dashboard'),

    # Proformas
    path('proformas/', views.proforma_list, name='proforma_list'),
    path('proformas/nouveau/', views.proforma_create, name='proforma_create'),
    path('proformas/<int:pk>/', views.proforma_detail, name='proforma_detail'),
    path('proformas/<int:pk>/modifier/', views.proforma_edit, name='proforma_edit'),
    path('proformas/<int:pk>/supprimer/', views.proforma_delete, name='proforma_delete'),
    path('proformas/<int:pk>/imprimer/', views.proforma_print, name='proforma_print'),
    path('proformas/<int:pk>/convertir/', views.proforma_to_invoice, name='proforma_to_invoice'),
    path('proformas/<int:pk>/statut/', views.proforma_status, name='proforma_status'),

    # Factures
    path('', views.invoice_list, name='invoice_list'),
    path('nouveau/', views.invoice_create, name='invoice_create'),
    path('<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('<int:pk>/modifier/', views.invoice_edit, name='invoice_edit'),
    path('<int:pk>/supprimer/', views.invoice_delete, name='invoice_delete'),
    path('<int:pk>/imprimer/', views.invoice_print, name='invoice_print'),
    path('<int:pk>/statut/', views.invoice_status, name='invoice_status'),
]
