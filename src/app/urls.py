from django.urls import path
from . import views, ctams_views

urlpatterns = [
    path('', views.home, name='home'),
    path('sw.js', views.service_worker, name='service_worker'),
    path('offline/', views.offline, name='offline'),
    path('contact-messages/', ctams_views.contact_message_list, name='submitted_contact_message_list'),
]
