from django.contrib.auth import get_user_model

User = get_user_model()


def get_active_users():
    return User.objects.filter(is_active=True).select_related('userprofile')
