import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse


class SubmittedQuoteListTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="atelier-user", password="test-pass")
        self.url = reverse("submitted_quote_list")

    def test_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth/login/", response["Location"])

    @override_settings(
        CTAMS_QUOTES_API_URL="https://ctams.example/internal-api/quote-requests/",
        CTAMS_QUOTES_API_KEY="test-shared-key",
    )
    @patch("quotes.views.urlopen")
    def test_reads_and_displays_submitted_requests_from_ctams(self, mock_urlopen):
        mock_response = mock_urlopen.return_value.__enter__.return_value
        mock_response.read.return_value = json.dumps({"results": [{
            "id": 7,
            "company_name": "Entreprise Démo",
            "contact_name": "Awa Koné",
            "email": "awa@example.ci",
            "phone": "0700000000",
            "vehicle_count": 12,
            "service_type": "contrat_flotte",
            "message": "Entretien annuel",
            "is_processed": False,
            "created_at": "2026-11-05T09:30:00Z",
        }]}).encode("utf-8")
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Entreprise Démo")
        self.assertContains(response, "Awa Koné")
        self.assertContains(response, "Entretien annuel")
        api_request = mock_urlopen.call_args.args[0]
        self.assertEqual(api_request.get_method(), "GET")
        self.assertEqual(api_request.get_header("X-api-key"), "test-shared-key")

    @override_settings(CTAMS_QUOTES_API_URL="", CTAMS_QUOTES_API_KEY="")
    def test_shows_configuration_error_without_calling_external_api(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "n’est pas configurée")
