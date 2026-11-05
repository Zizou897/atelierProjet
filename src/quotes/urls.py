from django.urls import path
from . import views

urlpatterns = [
    path("", views.submitted_quote_list, name="submitted_quote_list"),
]
