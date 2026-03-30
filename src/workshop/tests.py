from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from vehicles.models import Vehicle
from workshop.models import Maintenance, WorkshopVisit


class WorkshopVisitFlowTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="tech1", password="pass1234")
        self.vehicle = Vehicle.objects.create(
            registration_number="BB-456-BB",
            make="Peugeot",
            model="208",
            fuel_type="ESSENCE",
            transmission="MANUAL",
            mileage=45000,
            owner_name="Owner Test",
        )

    def test_create_visit_from_vehicle(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("vehicle_visit_create", kwargs={"vehicle_id": self.vehicle.id}),
            {
                "mileage_at_visit": 45120,
                "service": "CLIMATISATION",
                "concern": "Revision annuelle",
                "status": "DONE",
                "technician_name": "Tech One",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(WorkshopVisit.objects.count(), 1)
        self.assertEqual(Maintenance.objects.count(), 1)

        visit = WorkshopVisit.objects.get()
        self.assertIsNotNone(visit.maintenance)
        self.assertEqual(visit.service, WorkshopVisit.ServiceType.CLIMATISATION)
        self.assertEqual(visit.start_date, timezone.localdate())
        self.assertEqual(visit.end_date, timezone.localdate())
        self.assertEqual(visit.maintenance.status, Maintenance.MaintenanceStatus.DONE)
        self.assertEqual(visit.maintenance.vehicle_id, self.vehicle.id)
        self.assertIn("Climatisation", visit.maintenance.notes)

        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.mileage, 45120)

    def test_workshop_dashboard_period_filter(self):
        WorkshopVisit.objects.create(
            vehicle=self.vehicle,
            visit_date="2026-02-23",
            mileage_at_visit=45200,
            concern="Freinage",
            technician_name="Tech One",
            status="IN_PROGRESS",
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("workshop_dashboard"), {"period": "7"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard Atelier")
        self.assertContains(response, "Derniers 7 jours")

    def test_cannot_create_new_visit_if_previous_not_finished(self):
        WorkshopVisit.objects.create(
            vehicle=self.vehicle,
            visit_date="2026-02-20",
            mileage_at_visit=45050,
            service=WorkshopVisit.ServiceType.MECHANIQUE,
            concern="Freinage",
            status=WorkshopVisit.VisitStatus.IN_PROGRESS,
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("vehicle_visit_create", kwargs={"vehicle_id": self.vehicle.id}),
            {
                "mileage_at_visit": 45120,
                "service": "CLIMATISATION",
                "concern": "Revision annuelle",
                "status": "OPEN",
                "technician_name": "Tech One",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Impossible de creer un nouveau passage")
        self.assertEqual(WorkshopVisit.objects.count(), 1)
        self.assertEqual(Maintenance.objects.count(), 0)

    def test_update_visit_status_from_vehicle_sheet(self):
        maintenance = Maintenance.objects.create(
            vehicle=self.vehicle,
            opened_on="2026-02-20",
            status=Maintenance.MaintenanceStatus.OPEN,
            notes="Mecanique - Freinage",
        )
        visit = WorkshopVisit.objects.create(
            vehicle=self.vehicle,
            maintenance=maintenance,
            visit_date="2026-02-20",
            mileage_at_visit=45050,
            service=WorkshopVisit.ServiceType.MECHANIQUE,
            concern="Freinage",
            status=WorkshopVisit.VisitStatus.OPEN,
        )

        self.client.force_login(self.user)
        response = self.client.post(
            reverse(
                "vehicle_visit_update",
                kwargs={"vehicle_id": self.vehicle.id, "visit_id": visit.id},
            ),
            {
                "mileage_at_visit": 45100,
                "service": "MECHANIQUE",
                "concern": "Freinage",
                "diagnosis": "",
                "work_performed": "",
                "technician_name": "Tech One",
                "status": "DONE",
                "estimated_cost": "",
                "actual_cost": "",
                "next_visit_date": "",
            },
        )

        self.assertEqual(response.status_code, 302)
        visit.refresh_from_db()
        maintenance.refresh_from_db()
        self.assertEqual(visit.status, WorkshopVisit.VisitStatus.DONE)
        self.assertEqual(visit.end_date, timezone.localdate())
        self.assertEqual(maintenance.status, Maintenance.MaintenanceStatus.DONE)
