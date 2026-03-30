# Phase 3 : Modèle de Données V1

**Durée estimée**: 1-2 sprints  
**Dépendances**: ✅ Phase 2 complétée  
**Livrables**: Modèles + Migrations + Admin Django optimisé

---

## 📊 Stratégie

1. **Créer modèles** dans l'ordre de dépendance
2. **Générer migrations** progressivement
3. **Enregistrer admin** pour tests
4. **Tester intégrité référentielle**

---

## 1️⃣ App `users` - Authentification & Rôles

### Fichier: `src/users/models.py`

```python
from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.core.validators import MinValueValidator
from simple_history.models import HistoricalRecords

class CustomUser(AbstractUser):
    """
    Utilisateur personnalisé avec rôle et métadonnées
    """
    ROLES = [
        ('DG', 'Directeur Général'),
        ('ASSISTANT', 'Assistante/Accueil'),
        ('CHEF', 'Chef de Service'),
        ('TECH', 'Technicien'),
        ('COMPTA', 'Comptabilité'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLES, default='TECH')
    phone = models.CharField('Téléphone', max_length=20, blank=True)
    department = models.CharField('Département', max_length=100, blank=True)
    is_active_user = models.BooleanField('Actif', default=True)
    created_at = models.DateTimeField('Créé le', auto_now_add=True)
    updated_at = models.DateTimeField('Modifié le', auto_now=True)
    
    history = HistoricalRecords()
    
    class Meta:
        db_table = 'users_customuser'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['is_active_user']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def get_permissions(self):
        """Retourne les permissions du rôle"""
        groups = self.groups.all()
        return set(perm for group in groups 
                   for perm in group.permissions.all())
```

### Admin `src/users/admin.py`

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('CTAMS', {'fields': ('role', 'phone', 'department', 'is_active_user')}),
    )
    list_display = ('username', 'email', 'get_full_name', 'role', 'is_active_user')
    list_filter = BaseUserAdmin.list_filter + ('role',)
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
```

---

## 2️⃣ App `customers` - Clients

### Fichier: `src/customers/models.py`

```python
from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from simple_history.models import HistoricalRecords

class Client(models.Model):
    """
    Client particulier
    """
    # Identité
    first_name = models.CharField('Prénom', max_length=100)
    last_name = models.CharField('Nom', max_length=100)
    email = models.EmailField('Email', validators=[EmailValidator()])
    phone = models.CharField('Téléphone', max_length=20, unique=True)
    
    # Adresse
    address = models.CharField('Adresse', max_length=255)
    postal_code = models.CharField('Code postal', max_length=10)
    city = models.CharField('Ville', max_length=100)
    
    # Métadonnées
    created_at = models.DateTimeField('Créé le', auto_now_add=True)
    updated_at = models.DateTimeField('Modifié le', auto_now=True)
    created_by = models.ForeignKey('users.CustomUser', 
                                   on_delete=models.SET_NULL,
                                   null=True, related_name='clients_created')
    
    history = HistoricalRecords()
    
    class Meta:
        db_table = 'customers_client'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
        ]
    
    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.phone})"


class Company(models.Model):
    """
    Client entreprise
    """
    # Identité
    business_name = models.CharField('Raison sociale', max_length=255, unique=True)
    siret = models.CharField('SIRET', max_length=14, unique=True)
    
    # Contact principal
    contact_name = models.CharField('Personne contact', max_length=200)
    contact_email = models.EmailField('Email contact', validators=[EmailValidator()])
    contact_phone = models.CharField('Téléphone contact', max_length=20)
    
    # Adresse
    address = models.CharField('Adresse', max_length=255)
    postal_code = models.CharField('Code postal', max_length=10)
    city = models.CharField('Ville', max_length=100)
    
    # Conditions commerciales
    discount_rate = models.DecimalField('Remise (%)', max_digits=5, 
                                         decimal_places=2, default=0,
                                         validators=[MinValueValidator(0)])
    payment_terms = models.CharField('Conditions paiement', max_length=100, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField('Créé le', auto_now_add=True)
    updated_at = models.DateTimeField('Modifié le', auto_now=True)
    created_by = models.ForeignKey('users.CustomUser',
                                   on_delete=models.SET_NULL,
                                   null=True, related_name='companies_created')
    active = models.BooleanField('Actif', default=True)
    
    history = HistoricalRecords()
    
    class Meta:
        db_table = 'customers_company'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['siret']),
            models.Index(fields=['business_name']),
        ]
    
    def __str__(self):
        return f"{self.business_name} (SIRET: {self.siret})"
```

---

## 3️⃣ App `vehicles` - Parc Véhicules

### Fichier: `src/vehicles/models.py`

```python
from django.db import models
from simple_history.models import HistoricalRecords

class Vehicle(models.Model):
    """
    Véhicule unique identifié par immatriculation
    """
    # Identification
    registration = models.CharField('Immatriculation', max_length=20, 
                                   unique=True, db_index=True)
    vin = models.CharField('VIN', max_length=17, blank=True)
    
    # Infos techniques
    brand = models.CharField('Marque', max_length=50)
    model = models.CharField('Modèle', max_length=100)
    year = models.IntegerField('Année')
    fuel_type = models.CharField('Carburant', max_length=20, 
                                choices=[('ES', 'Essence'), ('GO', 'Diesel'),
                                        ('ELC', 'Électrique'), ('HYB', 'Hybride')])
    mileage = models.IntegerField('Kilométrage', default=0, 
                                 validators=[MinValueValidator(0)])
    
    # Métadonnées
    created_at = models.DateTimeField('Créé le', auto_now_add=True)
    updated_at = models.DateTimeField('Modifié le', auto_now=True)
    created_by = models.ForeignKey('users.CustomUser',
                                   on_delete=models.SET_NULL,
                                   null=True)
    
    history = HistoricalRecords()
    
    class Meta:
        db_table = 'vehicles_vehicle'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['registration']),
            models.Index(fields=['brand', 'model']),
        ]
    
    def __str__(self):
        return f"{self.brand} {self.model} ({self.registration})"


class VehicleOwnership(models.Model):
    """
    Liaison propriétaire (client ou entreprise) - véhicule
    """
    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE,
                               related_name='ownerships')
    
    # Propriétaire (client OU entreprise)
    client = models.ForeignKey('customers.Client', on_delete=models.CASCADE,
                              null=True, blank=True, related_name='vehicles')
    company = models.ForeignKey('customers.Company', on_delete=models.CASCADE,
                               null=True, blank=True, related_name='vehicles')
    
    # Dates propriété
    ownership_date = models.DateField('Date propriété')
    end_date = models.DateField('Date fin propriété', null=True, blank=True)
    
    is_primary = models.BooleanField('Propriétaire principal', default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'vehicles_ownership'
        constraints = [
            models.CheckConstraint(
                check=models.Q(client__isnull=False, company__isnull=True) |
                      models.Q(client__isnull=True, company__isnull=False),
                name='ownership_client_or_company'
            )
        ]
    
    def __str__(self):
        owner = self.client or self.company
        return f"{self.vehicle} → {owner}"
```

---

## 4️⃣ App `quotes` - Devis

### Fichier: `src/quotes/models.py`

```python
from django.db import models
from django.db.models import Sum, F
from decimal import Decimal
from simple_history.models import HistoricalRecords

class Quote(models.Model):
    """
    Devis avec numéro auto-généré
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Brouillon'),
        ('SENT', 'Envoyé'),
        ('SIGNED', 'Signé'),
        ('REFUSED', 'Refusé'),
        ('EXPIRED', 'Expiré'),
        ('VALIDATED', 'Validé'),
    ]
    
    # Numérotation
    quote_number = models.IntegerField('Numéro séquentiel', unique=True, db_index=True)
    quote_ref = models.CharField('Référence', max_length=20, unique=True, db_index=True)
    # Format: "DV-2026-000001"
    
    # Client & véhicule
    client = models.ForeignKey('customers.Client', on_delete=models.PROTECT,
                              null=True, blank=True, related_name='quotes')
    company = models.ForeignKey('customers.Company', on_delete=models.PROTECT,
                               null=True, blank=True, related_name='quotes')
    vehicle = models.ForeignKey('vehicles.Vehicle', on_delete=models.PROTECT,
                               related_name='quotes')
    
    # Infos financières
    tva_rate = models.DecimalField('Taux TVA (%)', max_digits=5, decimal_places=2, default=20)
    total_ht = models.DecimalField('Total HT', max_digits=12, decimal_places=2, default=0)
    total_tva = models.DecimalField('Total TVA', max_digits=12, decimal_places=2, default=0)
    total_ttc = models.DecimalField('Total TTC', max_digits=12, decimal_places=2, default=0)
    
    # Statut et dates
    status = models.CharField('Statut', max_length=10, choices=STATUS_CHOICES, 
                             default='DRAFT')
    created_date = models.DateTimeField('Date création', auto_now_add=True)
    validity_date = models.DateField('Date validité', null=True, blank=True)
    signed_date = models.DateTimeField('Date signature', null=True, blank=True)
    
    # Métadonnées
    description = models.TextField('Description', blank=True)
    created_by = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL,
                                   null=True, related_name='quotes_created')
    
    history = HistoricalRecords()
    
    class Meta:
        db_table = 'quotes_quote'
        ordering = ['-created_date']
        indexes = [
            models.Index(fields=['quote_ref']),
            models.Index(fields=['status']),
            models.Index(fields=['created_date']),
        ]
    
    def __str__(self):
        return f"{self.quote_ref} - {self.get_status_display()}"
    
    def recalculate_totals(self):
        """Recalcule les totaux HT/TVA/TTC"""
        self.total_ht = self.lines.aggregate(
            total=Sum(F('quantity') * F('unit_price'), 
                     output_field=models.DecimalField())
        )['total'] or Decimal('0')
        
        self.total_tva = self.total_ht * (self.tva_rate / 100)
        self.total_ttc = self.total_ht + self.total_tva
        self.save()


class QuoteLine(models.Model):
    """
    Ligne de devis (pièce, main-d'oeuvre, prestation)
    """
    quote = models.ForeignKey('Quote', on_delete=models.CASCADE,
                             related_name='lines')
    
    description = models.CharField('Description', max_length=255)
    line_type = models.CharField('Type', max_length=10,
                                choices=[('PART', 'Pièce'), 
                                        ('LABOR', 'Main-d\'oeuvre'),
                                        ('SERVICE', 'Prestation')])
    unit_price = models.DecimalField('Prix unitaire HT', max_digits=10, decimal_places=2)
    quantity = models.DecimalField('Quantité', max_digits=10, decimal_places=2, default=1)
    line_tva_rate = models.DecimalField('TVA (%)', max_digits=5, decimal_places=2, 
                                       default=20)
    
    order = models.PositiveIntegerField('Ordre', default=0)
    
    class Meta:
        db_table = 'quotes_quoteline'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.description} (x{self.quantity})"
    
    def get_line_total_ht(self):
        return self.quantity * self.unit_price


class QuoteSignature(models.Model):
    """
    Journal de signature du devis
    """
    quote = models.ForeignKey('Quote', on_delete=models.CASCADE,
                             related_name='signatures')
    
    signed_by = models.CharField('Signé par', max_length=200)
    signed_at = models.DateTimeField('Date/heure', auto_now_add=True)
    ip_address = models.GenericIPAddressField('Adresse IP')
    signature_type = models.CharField('Type signature', max_length=20,
                                     choices=[('EMAIL', 'Validation email'),
                                             ('DIGITAL', 'Signature numérique')])
    
    class Meta:
        db_table = 'quotes_signature'
        ordering = ['-signed_at']
    
    def __str__(self):
        return f"Signature {self.quote} par {self.signed_by}"
```

---

## 5️⃣ Checklist Intégrité Données

```python
# Vérifications à ajouter en migrations

class Migration(migrations.Migration):
    operations = [
        migrations.RunSQL(
            """
            CREATE SEQUENCE IF NOT EXISTS quote_seq START 1;
            CREATE TRIGGER update_quote_ref
            BEFORE INSERT ON quotes_quote
            FOR EACH ROW
            BEGIN
                IF NEW.quote_number IS NULL THEN
                    NEW.quote_number := nextval('quote_seq');
                END IF;
                NEW.quote_ref := 'DV-' || EXTRACT(YEAR FROM NOW()) || '-' 
                                || LPAD(NEW.quote_number::TEXT, 6, '0');
            END;
            """
        ),
    ]
```

---

## 🚀 Commandes Phase 3

```bash
# 1. Créer migrations customuser
python manage.py makemigrations users

# 2. Créer migrations customers
python manage.py makemigrations customers

# 3. Créer migrations vehicles
python manage.py makemigrations vehicles

# 4. Créer migrations quotes (et invoices, workshop, etc.)
python manage.py makemigrations

# 5. Appliquer toutes migrations
python manage.py migrate

# 6. Vérifier
python manage.py check

# 7. Tester imports
python manage.py shell
>>> from customers.models import Client
>>> Client.objects.count()
```

---

## 📋 Livrables Phase 3

- ✅ 7 models.py complets avec validations
- ✅ Admin Django enregistré
- ✅ Migrations stables
- ✅ Contraintes DB (unique, FK, check)
- ✅ Audit logs (via django-simple-history)
- ✅ Tests modèles basiques

---

**Prêt pour Phase 5 : Serializers DRF!** 🎯
