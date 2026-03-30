from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from vehicles.models import Vehicle


class Maintenance(models.Model):
    class MaintenanceStatus(models.TextChoices):
        OPEN = "OPEN", "Ouverte"
        DONE = "DONE", "Terminee"
        CANCELED = "CANCELED", "Annulee"

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="maintenances",
        verbose_name="Vehicule",
    )
    opened_on = models.DateField("Date de maintenance", default=timezone.localdate)
    status = models.CharField(
        "Statut maintenance",
        max_length=20,
        choices=MaintenanceStatus.choices,
        default=MaintenanceStatus.OPEN,
    )
    notes = models.TextField("Notes maintenance", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-opened_on", "-id"]

    def __str__(self):
        return f"{self.vehicle.registration_number} - maintenance du {self.opened_on}"


class WorkshopVisit(models.Model):
    class ServiceType(models.TextChoices):
        MECHANIQUE = "MECHANIQUE", "Mecanique"
        CLIMATISATION = "CLIMATISATION", "Climatisation"
        PNEUMATIQUES = "PNEUMATIQUES", "Pneumatiques"
        TOLERIE_SOUDURE = "TOLERIE_SOUDURE", "Tolerie/soudure"
        ELECTRICITE = "ELECTRICITE", "Electricite"
        SCANNER_AUTO = "SCANNER_AUTO", "Scanner Auto"

    class VisitStatus(models.TextChoices):
        OPEN = "OPEN", "Ouvert"
        IN_PROGRESS = "IN_PROGRESS", "En cours"
        DONE = "DONE", "Termine"
        CANCELED = "CANCELED", "Annule"

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="workshop_visits",
        verbose_name="Vehicule",
    )
    maintenance = models.ForeignKey(
        Maintenance,
        on_delete=models.CASCADE,
        related_name="services",
        verbose_name="Maintenance rattachee",
        blank=True,
        null=True,
    )
    visit_date = models.DateField("Date de passage", default=timezone.localdate)
    start_date = models.DateField("Date de debut", default=timezone.localdate)
    end_date = models.DateField("Date de fin", blank=True, null=True)
    mileage_at_visit = models.PositiveIntegerField(
        "Kilometrage lors du passage",
        validators=[MinValueValidator(0)],
    )
    service = models.CharField(
        "Service atelier",
        max_length=30,
        choices=ServiceType.choices,
        default=ServiceType.MECHANIQUE,
    )
    concern = models.CharField("Motif principal", max_length=255)
    diagnosis = models.TextField("Diagnostic", blank=True)
    work_performed = models.TextField("Travaux effectues", blank=True)
    technician_name = models.CharField("Technicien", max_length=120, blank=True)
    status = models.CharField(
        "Statut",
        max_length=20,
        choices=VisitStatus.choices,
        default=VisitStatus.OPEN,
    )
    estimated_cost = models.DecimalField(
        "Cout estime",
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    actual_cost = models.DecimalField(
        "Cout reel",
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    next_visit_date = models.DateField("Prochain passage suggere", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-visit_date", "-id"]

    def __str__(self):
        return f"{self.vehicle.registration_number} - {self.visit_date}"


class Technician(models.Model):
    first_name = models.CharField("Prénom", max_length=80)
    last_name = models.CharField("Nom", max_length=80)
    position = models.CharField("Poste", max_length=80)
    contact = models.CharField("Contact", max_length=120)
    identification_number = models.CharField("N° identification", max_length=40, unique=True)
    atelier = models.CharField(
        "Atelier",
        max_length=120,
        blank=True,
        choices=WorkshopVisit.ServiceType.choices,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Technicien"
        verbose_name_plural = "Techniciens"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
