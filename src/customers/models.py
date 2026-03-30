from django.db import models


class Customer(models.Model):
    class CustomerType(models.TextChoices):
        INDIVIDUAL = "INDIVIDUAL", "Particulier"
        COMPANY = "COMPANY", "Entreprise"

    customer_type = models.CharField(
        max_length=20,
        choices=CustomerType.choices,
        default=CustomerType.INDIVIDUAL,
    )
    first_name = models.CharField(max_length=80, blank=True)
    last_name = models.CharField(max_length=80, blank=True)
    company_name = models.CharField(max_length=150, blank=True)

    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)

    address_line1 = models.CharField(max_length=180, blank=True)
    address_line2 = models.CharField(max_length=180, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=80, blank=True)
    country = models.CharField(max_length=80, blank=True, default="France")

    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["company_name", "last_name", "first_name", "id"]

    @property
    def display_name(self):
        if self.customer_type == self.CustomerType.COMPANY:
            return self.company_name or "Entreprise sans nom"
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or "Client sans nom"

    def __str__(self):
        return self.display_name
