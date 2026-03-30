from django.core.validators import MinValueValidator
from django.db import models

from customers.models import Customer


class Vehicle(models.Model):
    class FuelType(models.TextChoices):
        ESSENCE = "ESSENCE", "Essence"
        DIESEL = "DIESEL", "Diesel"
        HYBRID = "HYBRID", "Hybride"
        ELECTRIC = "ELECTRIC", "Electrique"
        GPL = "GPL", "GPL"
        OTHER = "OTHER", "Autre"

    class TransmissionType(models.TextChoices):
        MANUAL = "MANUAL", "Manuelle"
        AUTO = "AUTO", "Automatique"
        ROBOT = "ROBOT", "Robotisee"
        OTHER = "OTHER", "Autre"

    registration_number = models.CharField(
        "Immatriculation",
        max_length=20,
        unique=True,
        db_index=True,
    )
    vin = models.CharField(
        "Numero de serie (VIN)",
        max_length=17,
        blank=True,
        null=True,
        unique=True,
    )
    make = models.CharField("Marque", max_length=80)
    model = models.CharField("Modele", max_length=80)
    trim = models.CharField("Finition", max_length=80, blank=True)
    first_registration_date = models.DateField(
        "Date de 1ere mise en circulation",
        blank=True,
        null=True,
    )
    fuel_type = models.CharField(
        "Carburant",
        max_length=20,
        choices=FuelType.choices,
        default=FuelType.ESSENCE,
    )
    transmission = models.CharField(
        "Transmission",
        max_length=20,
        choices=TransmissionType.choices,
        default=TransmissionType.MANUAL,
    )
    mileage = models.PositiveIntegerField(
        "Kilometrage actuel",
        default=0,
        validators=[MinValueValidator(0)],
    )
    color = models.CharField("Couleur", max_length=40, blank=True)

    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="vehicles",
        verbose_name="Client rattache",
    )

    owner_name = models.CharField("Nom proprietaire", max_length=120)
    owner_phone = models.CharField("Telephone proprietaire", max_length=30, blank=True)
    owner_email = models.EmailField("Email proprietaire", blank=True)

    notes = models.TextField("Notes techniques", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["registration_number"]

    def __str__(self):
        return f"{self.registration_number} - {self.make} {self.model}"
