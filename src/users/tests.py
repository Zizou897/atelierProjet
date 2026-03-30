"""Tests pour les vues d'authentification."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse

from .models import Role

User = get_user_model()


class LoginViewTests(TestCase):
    """Tests pour la vue de connexion."""

    def setUp(self):
        self.client = Client()
        self.login_url = reverse("login")
        self.dashboard_url = reverse("dashboard")

        self.test_user = User.objects.create_user(
            username="testuser",
            email="test@ctams.fr",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_login_page_loads(self):
        response = self.client.get(self.login_url)
        assert response.status_code == 200
        assert "CTAMS" in response.content.decode()

    def test_login_valid_credentials(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "testuser",
                "password": "testpass123",
            },
            follow=True,
        )
        assert response.status_code == 200
        assert response.wsgi_request.user.is_authenticated

    def test_login_invalid_credentials(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "testuser",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401

    def test_logout(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("logout"), follow=True)
        assert response.status_code == 200
        assert not response.wsgi_request.user.is_authenticated

    def test_superuser_cannot_login_from_portal(self):
        User.objects.create_superuser(
            username="admin",
            email="admin@ctams.fr",
            password="admin",
        )
        response = self.client.post(
            self.login_url,
            {
                "username": "admin",
                "password": "admin",
            },
        )
        assert response.status_code == 403
        assert "ne sont pas autorises" in response.content.decode()


class SecurityTests(TestCase):
    """Tests de securite basiques."""

    def setUp(self):
        self.client = Client()
        self.login_url = reverse("login")

    def test_csrf_token_present(self):
        response = self.client.get(self.login_url)
        assert "csrftoken" in response.content.decode()

    def test_password_field_type(self):
        response = self.client.get(self.login_url)
        content = response.content.decode()
        assert 'type="password"' in content


class UserManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.role = Role.objects.get(code="CHEF")

        self.manager = User.objects.create_user(username="manager", password="pass12345")
        permission = Permission.objects.get(codename="manage_users")
        self.manager.user_permissions.add(permission)

        self.user_no_perm = User.objects.create_user(username="noperm", password="pass12345")

    def test_user_list_requires_permission(self):
        url = reverse("user_list")

        response = self.client.get(url)
        assert response.status_code == 302

        self.client.force_login(self.user_no_perm)
        response = self.client.get(url)
        assert response.status_code == 403

        self.client.force_login(self.manager)
        response = self.client.get(url)
        assert response.status_code == 200

    def test_create_user_with_role(self):
        self.client.force_login(self.manager)

        response = self.client.post(
            reverse("user_create"),
            {
                "username": "newtech",
                "email": "newtech@ctams.fr",
                "first_name": "New",
                "last_name": "Tech",
                "role": self.role.id,
                "is_active": "on",
                "portal_active": "on",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
            },
        )
        assert response.status_code == 302

        created = User.objects.get(username="newtech")
        assert created.profile.role == self.role
