from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from customers.models import Customer


class ProformaStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Brouillon'
    SENT = 'SENT', 'Envoyé'
    ACCEPTED = 'ACCEPTED', 'Accepté'
    REJECTED = 'REJECTED', 'Rejeté'
    CONVERTED = 'CONVERTED', 'Converti en facture'


class InvoiceStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Brouillon'
    SENT = 'SENT', 'Envoyé'
    PARTIAL = 'PARTIAL', 'Partiellement payé'
    PAID = 'PAID', 'Payé'
    OVERDUE = 'OVERDUE', 'En retard'
    CANCELLED = 'CANCELLED', 'Annulé'


class Proforma(models.Model):
    numero = models.CharField(max_length=20, unique=True, editable=False, verbose_name='N° Proforma')
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='proformas', verbose_name='Client',
    )
    destinataire_nom = models.CharField(max_length=200, blank=True, verbose_name='Nom / Entreprise')
    destinataire_adresse = models.CharField(max_length=300, blank=True, verbose_name='Adresse')
    destinataire_tel = models.CharField(max_length=30, blank=True, verbose_name='Téléphone')
    destinataire_email = models.EmailField(blank=True, verbose_name='Email')
    destinataire_rccm_ncc = models.CharField(max_length=100, blank=True, verbose_name='RCCM / NCC')

    date_emission = models.DateField(default=timezone.now, verbose_name="Date d'émission")
    date_validite = models.DateField(null=True, blank=True, verbose_name="Valide jusqu'au")
    reference_client = models.CharField(max_length=100, blank=True, verbose_name='Référence client')
    objet = models.CharField(max_length=200, blank=True, verbose_name='Objet')
    bon_de_commande = models.CharField(max_length=100, blank=True, verbose_name='Bon de commande')

    remise_globale = models.DecimalField(
        max_digits=12, decimal_places=0, default=0, verbose_name='Remise globale (FCFA)',
    )
    tva_taux = models.DecimalField(
        max_digits=5, decimal_places=2, default=18, verbose_name='TVA (%)',
    )
    status = models.CharField(
        max_length=20, choices=ProformaStatus.choices, default=ProformaStatus.DRAFT,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='proformas_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_emission', '-id']
        verbose_name = 'Facture Proforma'
        verbose_name_plural = 'Factures Proforma'

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self._generate_numero()
        super().save(*args, **kwargs)

    @classmethod
    def _generate_numero(cls):
        year = timezone.now().year
        prefix = f"PF-{year}-"
        last = cls.objects.filter(numero__startswith=prefix).order_by('-id').first()
        if last:
            try:
                n = int(last.numero.rsplit('-', 1)[-1])
                return f"{prefix}{n + 1:03d}"
            except ValueError:
                pass
        return f"{prefix}001"

    @property
    def sous_total_ht(self):
        return sum((line.montant for line in self.lines.all()), 0)

    @property
    def net_ht(self):
        return max(self.sous_total_ht - int(self.remise_globale or 0), 0)

    @property
    def tva_montant(self):
        if self.tva_taux:
            return round(self.net_ht * self.tva_taux / 100)
        return 0

    @property
    def total_ttc(self):
        return self.net_ht + self.tva_montant

    def __str__(self):
        return self.numero


class ProformaLine(models.Model):
    proforma = models.ForeignKey(Proforma, on_delete=models.CASCADE, related_name='lines')
    ordre = models.PositiveSmallIntegerField(default=1)
    designation = models.CharField(max_length=300, verbose_name='Désignation')
    quantite = models.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name='Qté')
    prix_unitaire = models.DecimalField(
        max_digits=12, decimal_places=0, default=0, verbose_name='Prix unitaire (FCFA)',
    )

    class Meta:
        ordering = ['ordre']

    @property
    def montant(self):
        if self.quantite and self.prix_unitaire:
            return round(self.quantite * self.prix_unitaire)
        return 0

    def __str__(self):
        return f"{self.proforma.numero} – L{self.ordre}"


class Invoice(models.Model):
    numero = models.CharField(max_length=20, unique=True, editable=False, verbose_name='N° Facture')
    proforma = models.ForeignKey(
        Proforma, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='invoices', verbose_name="Proforma d'origine",
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='invoices', verbose_name='Client',
    )
    destinataire_nom = models.CharField(max_length=200, blank=True, verbose_name='Nom / Entreprise')
    destinataire_adresse = models.CharField(max_length=300, blank=True, verbose_name='Adresse')
    destinataire_tel = models.CharField(max_length=30, blank=True, verbose_name='Téléphone')
    destinataire_email = models.EmailField(blank=True, verbose_name='Email')
    destinataire_rccm_ncc = models.CharField(max_length=100, blank=True, verbose_name='RCCM / NCC')

    date_emission = models.DateField(default=timezone.now, verbose_name="Date d'émission")
    date_echeance = models.DateField(null=True, blank=True, verbose_name="Date d'échéance")
    reference_client = models.CharField(max_length=100, blank=True, verbose_name='Référence client')
    objet = models.CharField(max_length=200, blank=True, verbose_name='Objet')
    bon_de_commande = models.CharField(max_length=100, blank=True, verbose_name='Bon de commande')

    remise_globale = models.DecimalField(
        max_digits=12, decimal_places=0, default=0, verbose_name='Remise globale (FCFA)',
    )
    tva_taux = models.DecimalField(
        max_digits=5, decimal_places=2, default=18, verbose_name='TVA (%)',
    )
    acompte_verse = models.DecimalField(
        max_digits=12, decimal_places=0, default=0, verbose_name='Acompte versé (FCFA)',
    )
    conditions_paiement = models.TextField(
        blank=True,
        default='30 jours net à réception de facture / Chèque, virement ou espèces',
        verbose_name='Conditions de paiement',
    )
    penalites_retard = models.TextField(
        blank=True,
        default='Tout retard de paiement entraîne des pénalités de 1,5% par mois.',
        verbose_name='Pénalités de retard',
    )
    status = models.CharField(
        max_length=20, choices=InvoiceStatus.choices, default=InvoiceStatus.DRAFT,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='invoices_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_emission', '-id']
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self._generate_numero()
        super().save(*args, **kwargs)

    @classmethod
    def _generate_numero(cls):
        year = timezone.now().year
        prefix = f"FA-{year}-"
        last = cls.objects.filter(numero__startswith=prefix).order_by('-id').first()
        if last:
            try:
                n = int(last.numero.rsplit('-', 1)[-1])
                return f"{prefix}{n + 1:03d}"
            except ValueError:
                pass
        return f"{prefix}001"

    @property
    def sous_total_ht(self):
        return sum((line.montant for line in self.lines.all()), 0)

    @property
    def net_ht(self):
        return max(self.sous_total_ht - int(self.remise_globale or 0), 0)

    @property
    def tva_montant(self):
        if self.tva_taux:
            return round(self.net_ht * self.tva_taux / 100)
        return 0

    @property
    def total_ttc(self):
        return self.net_ht + self.tva_montant

    @property
    def net_a_payer(self):
        return max(self.total_ttc - int(self.acompte_verse or 0), 0)

    def __str__(self):
        return self.numero


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='lines')
    ordre = models.PositiveSmallIntegerField(default=1)
    designation = models.CharField(max_length=300, verbose_name='Désignation')
    quantite = models.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name='Qté')
    unite = models.CharField(max_length=30, blank=True, verbose_name='Unité')
    prix_unitaire = models.DecimalField(
        max_digits=12, decimal_places=0, default=0, verbose_name='Prix unitaire (FCFA)',
    )
    remise_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, verbose_name='Remise %',
    )

    class Meta:
        ordering = ['ordre']

    @property
    def montant(self):
        if self.quantite and self.prix_unitaire:
            remise = self.remise_pct if self.remise_pct else Decimal('0')
            coeff = (Decimal('100') - remise) / Decimal('100')
            return round(self.quantite * self.prix_unitaire * coeff)
        return 0

    def __str__(self):
        return f"{self.invoice.numero} – L{self.ordre}"
