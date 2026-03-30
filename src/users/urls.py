from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('contact-admin/', views.contact_admin_view, name='contact_admin'),
    path('users/', views.user_list_view, name='user_list'),
    path('users/new/', views.user_create_view, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_update_view, name='user_update'),
    path('roles/', views.role_list_view, name='role_list'),
]
