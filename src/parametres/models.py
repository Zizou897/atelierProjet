from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.templatetags.static import static
from simple_history.models import HistoricalRecords

DEFAULT_CONDITIONS = '30 jours net à réception de facture / Chèque, virement ou espèces'
DEFAULT_PENALITES = 'Tout retard de paiement entraîne des pénalités de 1,5% par mois.'


class CompanyProfile(models.Model):
    """Identité d'une entreprise émettrice (une ligne par marque : ctams, cta)."""

    DEFAULT_LOGOS = {
        'ctams': 'app/assets/img/ctams-logo.jpg',
        'cta': 'app/assets/img/cta-logo.png',
    }
    FALLBACK_LOGO = 'app/assets/img/ctams-logo.jpg'

    key = models.SlugField(max_length=20, unique=True)
    name = models.CharField(max_length=80, verbose_name='Nom')
    tag = models.CharField(max_length=150, blank=True, verbose_name='Slogan')
    full_name = models.CharField(max_length=200, verbose_name='Nom complet')
    address = models.CharField(max_length=255, verbose_name='Adresse')
    tel = models.CharField(max_length=100, verbose_name='Téléphone(s)')
    email = models.EmailField(verbose_name='Email')
    signataire = models.CharField(max_length=150, blank=True, verbose_name='Signataire')

    rccm = models.CharField(max_length=100, blank=True, verbose_name='RCCM')
    ncc = models.CharField(max_length=100, blank=True, verbose_name='NCC')

    bank_name = models.CharField(max_length=100, blank=True, verbose_name='Banque')
    bank_account = models.CharField(max_length=100, blank=True, verbose_name='IBAN / RIB')
    mobile_money = models.CharField(max_length=150, blank=True, verbose_name='Mobile Money')

    logo = models.ImageField(
        upload_to='logos/', blank=True, verbose_name='Logo',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
    )

    history = HistoricalRecords()

    class Meta:
        ordering = ['key']

    def __str__(self):
        return self.name

    @property
    def logo_url(self):
        if self.logo:
            return self.logo.url
        return static(self.DEFAULT_LOGOS.get(self.key, self.FALLBACK_LOGO))

    def as_brand(self):
        """Dictionnaire utilisé par les modèles d'impression (`brand.xxx`)."""
        return {
            'key': self.key,
            'name': self.name,
            'tag': self.tag,
            'full_name': self.full_name,
            'address': self.address,
            'tel': self.tel,
            'email': self.email,
            'signataire': self.signataire,
            'rccm': self.rccm,
            'ncc': self.ncc,
            'bank_name': self.bank_name,
            'bank_account': self.bank_account,
            'mobile_money': self.mobile_money,
            'logo_url': self.logo_url,
        }


class DocumentDefaults(models.Model):
    """Valeurs par défaut des nouveaux documents (une seule ligne)."""

    tva_taux = models.DecimalField(
        max_digits=5, decimal_places=2, default=18, verbose_name='TVA par défaut (%)',
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    conditions_paiement = models.TextField(
        blank=True, default=DEFAULT_CONDITIONS, verbose_name='Conditions de paiement',
    )
    penalites_retard = models.TextField(
        blank=True, default=DEFAULT_PENALITES, verbose_name='Pénalités de retard',
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Valeurs par défaut des documents'
        verbose_name_plural = 'Valeurs par défaut des documents'

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
