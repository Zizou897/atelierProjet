import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse


class ContactMessageListTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="contact-reader", password="test-pass")
        self.url = reverse("submitted_contact_message_list")

    def test_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth/login/", response["Location"])

    @override_settings(
        CTAMS_CONTACT_MESSAGES_API_URL="https://ctams.example/internal-api/contact-messages/",
        CTAMS_CONTACT_MESSAGES_API_KEY="test-shared-key",
    )
    @patch("app.ctams_views.urlopen")
    def test_reads_and_displays_contact_messages_from_ctams(self, mock_urlopen):
        mock_response = mock_urlopen.return_value.__enter__.return_value
        mock_response.read.return_value = json.dumps({"results": [{
            "id": 4,
            "name": "Awa Koné",
            "email": "awa@example.ci",
            "phone": "0700000000",
            "message": "Je souhaite être rappelée.",
            "is_read": False,
            "created_at": "2026-11-05T09:30:00Z",
        }]}).encode("utf-8")
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Awa Koné")
        self.assertContains(response, "Je souhaite être rappelée.")
        self.assertContains(response, "Nouveau")
        api_request = mock_urlopen.call_args.args[0]
        self.assertEqual(api_request.get_method(), "GET")
        self.assertEqual(api_request.get_header("X-api-key"), "test-shared-key")

    @override_settings(CTAMS_CONTACT_MESSAGES_API_URL="", CTAMS_CONTACT_MESSAGES_API_KEY="")
    def test_shows_configuration_error_when_api_is_not_configured(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "n’est pas configurée")
