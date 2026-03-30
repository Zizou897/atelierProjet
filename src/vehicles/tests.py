from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Vehicle


class VehicleFlowTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="agent1", password="pass1234")

    def test_vehicle_create_and_detail_flow(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("vehicle_create"),
            {
                "registration_number": "AA-123-AA",
                "vin": "VF1AAAAA123456789",
                "make": "Renault",
                "model": "Clio",
                "trim": "Business",
                "fuel_type": "DIESEL",
                "transmission": "MANUAL",
                "mileage": 120000,
                "owner_name": "Client Test",
            },
        )
        self.assertEqual(response.status_code, 302)

        vehicle = Vehicle.objects.get(registration_number="AA-123-AA")
        detail = self.client.get(reverse("vehicle_detail", kwargs={"vehicle_id": vehicle.id}))
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "Fiche technique")

    def test_vehicle_dashboard_period_filter(self):
        Vehicle.objects.create(
            registration_number="DD-111-DD",
            make="Toyota",
            model="Yaris",
            fuel_type="ESSENCE",
            transmission="MANUAL",
            mileage=72000,
            owner_name="Owner Two",
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("vehicle_dashboard"), {"period": "7"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard Vehicules")
        self.assertContains(response, "Derniers 7 jours")
