from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Customer
from vehicles.models import Vehicle

User = get_user_model()


class CustomerFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="custuser", password="pass12345")

    def test_create_and_open_customer(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("customer_create"),
            {
                "customer_type": "INDIVIDUAL",
                "first_name": "Jean",
                "last_name": "Martin",
                "email": "jean.martin@example.com",
                "phone": "0102030405",
                "city": "Paris",
                "country": "France",
                "is_active": "on",
            },
        )
        self.assertEqual(response.status_code, 302)

        customer = Customer.objects.get(email="jean.martin@example.com")
        detail = self.client.get(reverse("customer_detail", kwargs={"customer_id": customer.id}))
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "Jean Martin")

    def test_filter_customer_list_by_type(self):
        Customer.objects.create(
            customer_type="COMPANY",
            company_name="Garage Elite",
            email="contact@elite.fr",
        )
        Customer.objects.create(
            customer_type="INDIVIDUAL",
            first_name="Paul",
            last_name="Durand",
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("customer_list"), {"type": "COMPANY"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Garage Elite")
        self.assertNotContains(response, "Paul Durand")

    def test_customer_detail_shows_linked_vehicles(self):
        customer = Customer.objects.create(
            customer_type="COMPANY",
            company_name="Auto Fleet",
            email="contact@autofleet.fr",
        )
        Vehicle.objects.create(
            customer=customer,
            registration_number="CC-789-CC",
            make="Renault",
            model="Kangoo",
            fuel_type="DIESEL",
            transmission="MANUAL",
            mileage=98000,
            owner_name="Auto Fleet",
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("customer_detail", kwargs={"customer_id": customer.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CC-789-CC")

    def test_customer_dashboard_displays_dynamic_stats(self):
        Customer.objects.create(
            customer_type="COMPANY",
            company_name="Fleet One",
            city="Lyon",
            is_active=True,
        )
        Customer.objects.create(
            customer_type="INDIVIDUAL",
            first_name="Alice",
            last_name="Martin",
            city="Lyon",
            is_active=False,
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("customer_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard Clients")
        self.assertContains(response, "Clients totaux")

    def test_customer_dashboard_period_filter(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("customer_dashboard"), {"period": "7"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Derniers 7 jours")
