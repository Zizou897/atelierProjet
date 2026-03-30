from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Role(models.Model):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=80, unique=True)
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="users",
    )
    phone = models.CharField(max_length=30, blank=True)
    portal_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = [
            ("manage_users", "Can manage users, roles and permissions"),
        ]

    def __str__(self):
        role_name = self.role.name if self.role else "Sans role"
        return f"{self.user.username} - {role_name}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        UserProfile.objects.get_or_create(user=instance)
