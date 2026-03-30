from django.contrib import admin

from .models import Role, UserProfile


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "updated_at")
    search_fields = ("code", "name")
    list_filter = ("is_active",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "portal_active", "updated_at")
    search_fields = ("user__username", "user__email", "role__name")
    list_filter = ("portal_active", "role")
