# Page Paramètres Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Une page `/parametres/` (admins) pour modifier l'identité, le RCCM/NCC, le paiement et le logo de CTAMS et CTA, plus les valeurs par défaut des documents.

**Architecture:** Nouvelle app Django `parametres` avec deux modèles (`CompanyProfile`, une ligne par marque ; `DocumentDefaults`, une ligne). `invoices.branding.get_brand()` lit la base au lieu d'un dictionnaire en dur, avec repli sur ce dictionnaire. Les 3 modèles d'impression affichent les nouveaux champs ; les formulaires de création de facture et de proforma se pré-remplissent depuis `DocumentDefaults`.

**Tech Stack:** Django 6, django-simple-history (déjà installé), Pillow (à ajouter à requirements), tests `django.test.TestCase`. Spec : `docs/superpowers/specs/2026-10-27-parametres-design.md`.

**Conventions du projet :** commandes à lancer depuis `src/` avec `../venv/Scripts/python.exe manage.py ...` (Git Bash, Windows). Interface en français. Le garde d'accès admin existant est `@login_required(login_url="login")` + `@permission_required("users.manage_users", raise_exception=True)` (voir `src/users/views.py:250`).

**Écarts volontaires avec la spec (à refléter dans la spec, Task 0) :**
- `DocumentDefaults` est initialisé avec les textes actuels du modèle `Invoice` (conditions : « 30 jours net à réception de facture / Chèque, virement ou espèces », pénalités : « Tout retard de paiement entraîne des pénalités de 1,5% par mois. ») et non des textes vides, pour que rien ne change à la mise en service.
- Le proforma n'a pas de champs conditions/pénalités : il ne reçoit que la TVA par défaut. La facture reçoit les trois.
- `tag` et `signataire` sont facultatifs (seuls nom, nom complet, adresse, téléphone, email sont obligatoires, comme dans la spec).

---

## File Structure

| Fichier | Rôle |
|---|---|
| `src/parametres/__init__.py`, `apps.py` | app Django |
| `src/parametres/models.py` | `CompanyProfile`, `DocumentDefaults` |
| `src/parametres/migrations/0001_initial.py` | généré |
| `src/parametres/migrations/0002_seed_defaults.py` | données initiales (valeurs actuelles de `branding.py`) |
| `src/parametres/forms.py` | `CompanyProfileForm`, `DocumentDefaultsForm` |
| `src/parametres/views.py`, `urls.py` | vue `settings_home`, route `/parametres/` |
| `src/parametres/tests.py` | tests modèles, formulaires, vue |
| `src/templates/parametres/settings.html` | page à 3 onglets |
| `src/invoices/branding.py` | `get_brand()` lit la base |
| `src/invoices/views.py` | pré-remplissage depuis `DocumentDefaults` |
| `src/invoices/tests.py` | tests `get_brand`, impression, pré-remplissage |
| `src/templates/invoices/{invoice,proforma,delivery}_print.html` | logo + RCCM/NCC/paiement |
| `src/templates/base.html` | lien « Paramètres » |
| `src/core/settings.py`, `src/core/urls.py`, `requirements.txt` | enregistrement de l'app, route, Pillow |

---

### Task 0: Mettre à jour la spec et commiter le travail en attente

Le dépôt contient des modifications non commitées d'avant (champ RCCM/NCC client, « Multiservices »).

**Files:**
- Modify: `docs/superpowers/specs/2026-10-27-parametres-design.md`

- [ ] **Step 1: Commiter le RCCM/NCC client**

```bash
git add src/customers src/templates/customers src/templates/invoices/invoice_form.html src/templates/invoices/proforma_form.html src/templates/invoices/delivery_form.html
git commit -m "$(cat <<'EOF'
Ajout du champ RCCM/NCC pour les clients entreprise

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 2: Commiter l'orthographe « Multiservices »**

```bash
git add src/invoices/branding.py
git commit -m "$(cat <<'EOF'
Orthographe Multiservices dans les en-têtes de documents

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 3: Corriger la spec**

Dans la section « Données initiales » de la spec, remplacer la phrase « la ligne `DocumentDefaults` avec TVA 18 % et les textes vides » par « la ligne `DocumentDefaults` avec TVA 18 % et les conditions de paiement / pénalités actuelles du modèle `Invoice` ». Dans la section « Branchement sur l'existant », remplacer « Création d'une facture ou d'un proforma : `tva_taux`, `conditions_paiement` et `penalites_retard` sont pré-remplis » par « Création d'une facture : `tva_taux`, `conditions_paiement` et `penalites_retard` sont pré-remplis ; création d'un proforma : seulement `tva_taux` (le proforma n'a pas de conditions) ». Dans la table `CompanyProfile`, ajouter « , vide autorisé » à la ligne `tag` et `signataire`.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers
git commit -m "$(cat <<'EOF'
Précisions sur la spec Paramètres et plan d'implémentation

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 1: App `parametres`, modèles et données initiales

**Files:**
- Create: `src/parametres/__init__.py` (vide), `src/parametres/apps.py`, `src/parametres/models.py`, `src/parametres/tests.py`, `src/parametres/migrations/__init__.py` (vide), `src/parametres/migrations/0002_seed_defaults.py`
- Modify: `src/core/settings.py` (LOCAL_APPS), `requirements.txt`

- [ ] **Step 1: Ajouter Pillow aux dépendances**

Dans `requirements.txt`, sous la ligne `django-simple-history==3.11.0`, ajouter :

```
Pillow==12.0.0
```

- [ ] **Step 2: Créer l'app et l'enregistrer**

`src/parametres/apps.py` :

```python
from django.apps import AppConfig


class ParametresConfig(AppConfig):
    name = 'parametres'
```

Dans `src/core/settings.py`, ajouter `'parametres.apps.ParametresConfig',` à la fin de `LOCAL_APPS` (après `'users.apps.UsersConfig',`).

- [ ] **Step 3: Écrire les tests qui échouent**

`src/parametres/tests.py` :

```python
from django.test import TestCase

from .models import CompanyProfile, DocumentDefaults


class SeedDataTests(TestCase):
    def test_both_companies_are_seeded_with_current_values(self):
        ctams = CompanyProfile.objects.get(key='ctams')
        self.assertEqual(ctams.name, 'CTAMS')
        self.assertEqual(ctams.full_name, 'CENTRE TECHNIQUE AUTO & MULTISERVICES (CTAMS)')
        self.assertEqual(ctams.email, 'Sasava221@gmail.com')
        self.assertEqual(ctams.tel, '07 77 90 68 45 / 05 05 21 67 92')

        cta = CompanyProfile.objects.get(key='cta')
        self.assertEqual(cta.full_name, 'CENTRE TECHNIQUE AUTO (CTA)')
        self.assertEqual(cta.email, 'centretechniqueauto@outlook.com')

    def test_document_defaults_are_seeded(self):
        defaults = DocumentDefaults.load()
        self.assertEqual(defaults.tva_taux, 18)
        self.assertIn('30 jours net', defaults.conditions_paiement)
        self.assertIn('1,5%', defaults.penalites_retard)

    def test_logo_url_falls_back_to_static_file(self):
        cta = CompanyProfile.objects.get(key='cta')
        self.assertTrue(cta.logo_url.endswith('app/assets/img/cta-logo.png'))
        ctams = CompanyProfile.objects.get(key='ctams')
        self.assertTrue(ctams.logo_url.endswith('app/assets/img/ctams-logo.jpg'))

    def test_as_brand_exposes_all_template_keys(self):
        brand = CompanyProfile.objects.get(key='cta').as_brand()
        for key in ('key', 'name', 'tag', 'full_name', 'address', 'tel', 'email', 'signataire',
                    'rccm', 'ncc', 'bank_name', 'bank_account', 'mobile_money', 'logo_url'):
            self.assertIn(key, brand)
```

- [ ] **Step 4: Lancer les tests, vérifier l'échec**

Run: `cd src && ../venv/Scripts/python.exe manage.py test parametres`
Expected: erreur d'import (`cannot import name 'CompanyProfile'`).

- [ ] **Step 5: Écrire les modèles**

`src/parametres/models.py` :

```python
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
```

- [ ] **Step 6: Générer la migration de schéma**

Run: `cd src && ../venv/Scripts/python.exe manage.py makemigrations parametres`
Expected: `parametres\migrations\0001_initial.py` créé (inclut `CompanyProfile`, `DocumentDefaults` et leurs modèles `Historical...`).

- [ ] **Step 7: Écrire la migration de données**

`src/parametres/migrations/0002_seed_defaults.py` (valeurs figées, ne pas importer le code de l'application) :

```python
from django.db import migrations

COMPANIES = [
    {
        'key': 'ctams',
        'name': 'CTAMS',
        'tag': 'Centre Technique Auto & Multiservices',
        'full_name': 'CENTRE TECHNIQUE AUTO & MULTISERVICES (CTAMS)',
        'address': "Angré Nouveau CHU, Abidjan – Côte d'Ivoire",
        'tel': '07 77 90 68 45 / 05 05 21 67 92',
        'email': 'Sasava221@gmail.com',
        'signataire': 'M. Savadogo Salif — Gérant CTAMS',
    },
    {
        'key': 'cta',
        'name': 'CTA',
        'tag': 'Centre Technique Auto — Entretien & Réparation',
        'full_name': 'CENTRE TECHNIQUE AUTO (CTA)',
        'address': 'Riviera Bonoumin, Abidjan – non loin de la direction du marché public',
        'tel': '07 77 90 68 45 / 05 05 21 67 92',
        'email': 'centretechniqueauto@outlook.com',
        'signataire': 'M. Savadogo Salif — Gérant CTA',
    },
]


def seed(apps, schema_editor):
    CompanyProfile = apps.get_model('parametres', 'CompanyProfile')
    DocumentDefaults = apps.get_model('parametres', 'DocumentDefaults')
    for data in COMPANIES:
        CompanyProfile.objects.get_or_create(key=data['key'], defaults=data)
    DocumentDefaults.objects.get_or_create(pk=1)


class Migration(migrations.Migration):

    dependencies = [
        ('parametres', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
```

(`DocumentDefaults.objects.get_or_create(pk=1)` prend les `default=` du modèle figé dans 0001 : TVA 18 et les textes actuels.)

- [ ] **Step 8: Lancer les tests, vérifier le succès**

Run: `cd src && ../venv/Scripts/python.exe manage.py test parametres`
Expected: 4 tests OK.

- [ ] **Step 9: Commit**

```bash
git add requirements.txt src/core/settings.py src/parametres
git commit -m "$(cat <<'EOF'
Ajout de l'app parametres (profils d'entreprise et valeurs par défaut)

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: `get_brand()` lit la base

**Files:**
- Modify: `src/invoices/branding.py`
- Test: `src/invoices/tests.py`

- [ ] **Step 1: Écrire les tests qui échouent**

Remplacer le contenu de `src/invoices/tests.py` par :

```python
from django.test import RequestFactory, TestCase

from parametres.models import CompanyProfile

from .branding import get_brand


class GetBrandTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_reads_values_from_database(self):
        CompanyProfile.objects.filter(key='cta').update(
            tel='01 02 03', rccm='CI-ABJ-2020-B-1', ncc='1234567 A',
        )
        brand = get_brand(self.factory.get('/', {'marque': 'cta'}))
        self.assertEqual(brand['key'], 'cta')
        self.assertEqual(brand['tel'], '01 02 03')
        self.assertEqual(brand['rccm'], 'CI-ABJ-2020-B-1')
        self.assertEqual(brand['ncc'], '1234567 A')

    def test_unknown_or_missing_key_returns_ctams(self):
        self.assertEqual(get_brand(self.factory.get('/'))['key'], 'ctams')
        self.assertEqual(get_brand(self.factory.get('/', {'marque': 'zzz'}))['key'], 'ctams')

    def test_empty_database_falls_back_to_hardcoded_values(self):
        CompanyProfile.objects.all().delete()
        brand = get_brand(self.factory.get('/', {'marque': 'cta'}))
        self.assertEqual(brand['key'], 'cta')
        self.assertEqual(brand['email'], 'centretechniqueauto@outlook.com')
        self.assertEqual(brand['rccm'], '')
        self.assertTrue(brand['logo_url'].endswith('app/assets/img/cta-logo.png'))
```

- [ ] **Step 2: Lancer, vérifier l'échec**

Run: `cd src && ../venv/Scripts/python.exe manage.py test invoices`
Expected: `KeyError: 'rccm'` / `logo_url` (l'ancien `get_brand` ne renvoie pas ces clés).

- [ ] **Step 3: Réécrire `get_brand`**

Dans `src/invoices/branding.py`, remplacer le docstring du module et tout ce qui suit le dictionnaire `BRANDS` (de `DEFAULT_BRAND = 'ctams'` jusqu'à la fin) par ce qui suit. Conserver le dictionnaire `BRANDS` tel quel (il sert de repli si la base est vide).

Docstring du module :

```python
"""Profils de marque pour l'impression des documents (facture, proforma, bon de livraison).

Les valeurs sont modifiables dans Paramètres (modèle ``parametres.CompanyProfile``). Le
dictionnaire ``BRANDS`` ci-dessous n'est qu'un repli utilisé si la base ne contient pas
la ligne demandée. L'utilisateur choisit la marque au moment de l'impression via le
paramètre GET ``?marque=ctams|cta``.
"""
```

Imports en tête de fichier (après le docstring) :

```python
from django.templatetags.static import static

from parametres.models import CompanyProfile
```

Fin du fichier :

```python
DEFAULT_BRAND = 'ctams'


def _fallback_brand(key):
    data = dict(BRANDS.get(key, BRANDS[DEFAULT_BRAND]))
    data.update(
        rccm='', ncc='', bank_name='', bank_account='', mobile_money='',
        logo_url=static(data['logo']),
    )
    return data


def get_brand(request):
    """Retourne le profil de marque demandé (défaut : CTAMS)."""
    key = (request.GET.get('marque') or DEFAULT_BRAND).lower()
    profile = (
        CompanyProfile.objects.filter(key=key).first()
        or CompanyProfile.objects.filter(key=DEFAULT_BRAND).first()
    )
    return profile.as_brand() if profile else _fallback_brand(key)
```

- [ ] **Step 4: Lancer, vérifier le succès**

Run: `cd src && ../venv/Scripts/python.exe manage.py test invoices parametres`
Expected: tous OK.

- [ ] **Step 5: Commit**

```bash
git add src/invoices/branding.py src/invoices/tests.py
git commit -m "$(cat <<'EOF'
get_brand lit les profils d'entreprise en base

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Modèles d'impression (logo, RCCM/NCC, paiement)

**Files:**
- Modify: `src/templates/invoices/invoice_print.html`, `proforma_print.html`, `delivery_print.html`
- Test: `src/invoices/tests.py`

- [ ] **Step 1: Écrire les tests qui échouent**

Ajouter à `src/invoices/tests.py` (imports en tête : `from datetime import date`, `from django.contrib.auth import get_user_model`, `from django.urls import reverse`, `from .models import DeliveryNote, Invoice, Proforma`) :

```python
class PrintTemplatesTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='printer', password='pass12345')
        self.client.force_login(user)
        today = date.today()
        self.urls = {
            'invoice': reverse('invoice_print', args=[
                Invoice.objects.create(destinataire_nom='Client', date_emission=today).pk]),
            'proforma': reverse('proforma_print', args=[
                Proforma.objects.create(destinataire_nom='Client', date_emission=today).pk]),
            'delivery': reverse('delivery_print', args=[
                DeliveryNote.objects.create(destinataire_nom='Client', date_livraison=today).pk]),
        }

    def test_legal_and_payment_info_shown_when_filled(self):
        CompanyProfile.objects.filter(key='ctams').update(
            rccm='CI-ABJ-2020-B-1', ncc='1234567 A',
            bank_name='Banque Test', bank_account='CI93 0000', mobile_money='Wave 07 00 00 00 00',
        )
        for name, url in self.urls.items():
            html = self.client.get(url).content.decode()
            for text in ('CI-ABJ-2020-B-1', '1234567 A', 'Banque Test', 'CI93 0000', 'Wave 07 00 00 00 00'):
                self.assertIn(text, html, f'{text} absent de {name}')

    def test_nothing_shown_when_empty(self):
        for name, url in self.urls.items():
            html = self.client.get(url).content.decode()
            for label in ('RCCM :', 'NCC :', 'Banque :', 'Mobile Money :'):
                self.assertNotIn(label, html, f'{label} affiché sur {name}')

    def test_uploaded_logo_url_used_in_header(self):
        CompanyProfile.objects.filter(key='ctams').update(logo='logos/test.png')
        for name, url in self.urls.items():
            html = self.client.get(url).content.decode()
            self.assertIn('/media/logos/test.png', html, name)
```

Note : si un des `create(...)` échoue pour un champ obligatoire manquant, lire le modèle (`src/invoices/models.py`) et ajouter le champ nécessaire dans le test ; ne pas modifier le modèle.

- [ ] **Step 2: Lancer, vérifier l'échec**

Run: `cd src && ../venv/Scripts/python.exe manage.py test invoices.tests.PrintTemplatesTests`
Expected: FAIL (`CI-ABJ-2020-B-1` absent, `/media/logos/test.png` absent).

- [ ] **Step 3: Modifier les 3 modèles d'impression**

Dans chacun des trois fichiers `invoice_print.html`, `proforma_print.html`, `delivery_print.html` :

a) Remplacer l'attribut du logo :

```html
<img src="{% static brand.logo %}" alt="{{ brand.name }}">
```
par
```html
<img src="{{ brand.logo_url }}" alt="{{ brand.name }}">
```

b) Dans le bloc `party-box` « Émetteur » (indentation de 8 espaces ; ne pas toucher à l'en-tête, indenté de 10), remplacer

```html
        Email : <span class="brand-email">{{ brand.email }}</span>
      </div>
```
par
```html
        Email : <span class="brand-email">{{ brand.email }}</span>
        {% if brand.rccm %}<br>RCCM : {{ brand.rccm }}{% endif %}
        {% if brand.ncc %}<br>NCC : {{ brand.ncc }}{% endif %}
        {% if brand.bank_name %}<br>Banque : {{ brand.bank_name }}{% endif %}
        {% if brand.bank_account %}<br>IBAN / RIB : {{ brand.bank_account }}{% endif %}
        {% if brand.mobile_money %}<br>Mobile Money : {{ brand.mobile_money }}{% endif %}
      </div>
```

- [ ] **Step 4: Lancer, vérifier le succès**

Run: `cd src && ../venv/Scripts/python.exe manage.py test invoices`
Expected: tous OK.

- [ ] **Step 5: Commit**

```bash
git add src/templates/invoices src/invoices/tests.py
git commit -m "$(cat <<'EOF'
Impression : logo configurable, RCCM/NCC et coordonnées de paiement de l'émetteur

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Formulaires de réglages

**Files:**
- Create: `src/parametres/forms.py`
- Test: `src/parametres/tests.py`

- [ ] **Step 1: Écrire les tests qui échouent**

Ajouter à `src/parametres/tests.py` (imports : `import io`, `import shutil`, `import tempfile`, `from PIL import Image`, `from django.core.files.uploadedfile import SimpleUploadedFile`, `from django.test import override_settings`, `from .forms import CompanyProfileForm, DocumentDefaultsForm`) :

```python
def make_image(name='logo.png', fmt='PNG', size=(10, 10)):
    buf = io.BytesIO()
    Image.new('RGB', size, 'red').save(buf, fmt)
    return SimpleUploadedFile(name, buf.getvalue(), content_type=f'image/{fmt.lower()}')


def company_data(**overrides):
    data = {
        'name': 'CTA', 'tag': '', 'full_name': 'CENTRE TECHNIQUE AUTO (CTA)',
        'address': 'Riviera', 'tel': '01 02', 'email': 'cta@example.com', 'signataire': '',
        'rccm': 'CI-1', 'ncc': '123', 'bank_name': '', 'bank_account': '', 'mobile_money': '',
    }
    data.update(overrides)
    return data


class CompanyProfileFormTests(TestCase):
    def setUp(self):
        self.media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.media, ignore_errors=True)
        override = override_settings(MEDIA_ROOT=self.media)
        override.enable()
        self.addCleanup(override.disable)
        self.profile = CompanyProfile.objects.get(key='cta')

    def test_saves_valid_data(self):
        form = CompanyProfileForm(company_data(), instance=self.profile)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.rccm, 'CI-1')
        self.assertEqual(self.profile.ncc, '123')

    def test_required_fields(self):
        form = CompanyProfileForm(company_data(email='', tel='', address=''), instance=self.profile)
        self.assertFalse(form.is_valid())
        for field in ('email', 'tel', 'address'):
            self.assertIn(field, form.errors)

    def test_rejects_invalid_email(self):
        form = CompanyProfileForm(company_data(email='pas-un-email'), instance=self.profile)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_accepts_png_logo(self):
        form = CompanyProfileForm(company_data(), {'logo': make_image()}, instance=self.profile)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.logo.name.startswith('logos/'))

    def test_rejects_non_image_logo(self):
        fake = SimpleUploadedFile('logo.png', b'pas une image', content_type='image/png')
        form = CompanyProfileForm(company_data(), {'logo': fake}, instance=self.profile)
        self.assertFalse(form.is_valid())
        self.assertIn('logo', form.errors)

    def test_rejects_wrong_extension(self):
        form = CompanyProfileForm(company_data(), {'logo': make_image('logo.gif', 'GIF')}, instance=self.profile)
        self.assertFalse(form.is_valid())
        self.assertIn('logo', form.errors)

    def test_rejects_logo_over_2mb(self):
        big = SimpleUploadedFile('logo.png', make_image().read() + b'0' * (2 * 1024 * 1024), content_type='image/png')
        form = CompanyProfileForm(company_data(), {'logo': big}, instance=self.profile)
        self.assertFalse(form.is_valid())
        self.assertIn('logo', form.errors)

    def test_remove_logo_checkbox_restores_default(self):
        self.profile.logo = 'logos/old.png'
        self.profile.save()
        form = CompanyProfileForm(company_data(remove_logo='on'), instance=self.profile)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.logo)
        self.assertTrue(self.profile.logo_url.endswith('cta-logo.png'))


class DocumentDefaultsFormTests(TestCase):
    def test_saves_valid_data(self):
        form = DocumentDefaultsForm(
            {'tva_taux': '10', 'conditions_paiement': 'Comptant', 'penalites_retard': ''},
            instance=DocumentDefaults.load(),
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertEqual(DocumentDefaults.load().tva_taux, 10)

    def test_tva_must_be_between_0_and_100(self):
        for bad in ('-1', '101'):
            form = DocumentDefaultsForm(
                {'tva_taux': bad, 'conditions_paiement': '', 'penalites_retard': ''},
                instance=DocumentDefaults.load(),
            )
            self.assertFalse(form.is_valid(), bad)
            self.assertIn('tva_taux', form.errors)
```

- [ ] **Step 2: Lancer, vérifier l'échec**

Run: `cd src && ../venv/Scripts/python.exe manage.py test parametres`
Expected: erreur d'import (`parametres.forms` introuvable).

- [ ] **Step 3: Écrire les formulaires**

`src/parametres/forms.py` :

```python
from django import forms
from django.core.files.uploadedfile import UploadedFile

from .models import CompanyProfile, DocumentDefaults

MAX_LOGO_SIZE = 2 * 1024 * 1024


class CompanyProfileForm(forms.ModelForm):
    remove_logo = forms.BooleanField(required=False, label='Revenir au logo par défaut')

    class Meta:
        model = CompanyProfile
        fields = [
            'name', 'tag', 'full_name', 'address', 'tel', 'email', 'signataire',
            'rccm', 'ncc',
            'bank_name', 'bank_account', 'mobile_money',
            'logo',
        ]
        widgets = {
            'logo': forms.FileInput(attrs={'accept': 'image/jpeg,image/png,image/webp'}),
        }

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if isinstance(logo, UploadedFile) and logo.size > MAX_LOGO_SIZE:
            raise forms.ValidationError('Le logo ne doit pas dépasser 2 Mo.')
        return logo

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.cleaned_data.get('remove_logo') and 'logo' not in self.files:
            profile.logo = ''
        if commit:
            profile.save()
        return profile


class DocumentDefaultsForm(forms.ModelForm):
    class Meta:
        model = DocumentDefaults
        fields = ['tva_taux', 'conditions_paiement', 'penalites_retard']
        widgets = {
            'conditions_paiement': forms.Textarea(attrs={'rows': 3}),
            'penalites_retard': forms.Textarea(attrs={'rows': 3}),
        }
```

Les libellés viennent des `verbose_name` des modèles.

- [ ] **Step 4: Lancer, vérifier le succès**

Run: `cd src && ../venv/Scripts/python.exe manage.py test parametres`
Expected: tous OK. Si `test_rejects_non_image_logo` passe pour une autre raison que Pillow, c'est normal : `ImageField` rejette le contenu invalide.

- [ ] **Step 5: Commit**

```bash
git add src/parametres/forms.py src/parametres/tests.py
git commit -m "$(cat <<'EOF'
Formulaires des réglages (entreprise et valeurs par défaut)

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: Vue, route, page et lien du menu

**Files:**
- Create: `src/parametres/views.py`, `src/parametres/urls.py`, `src/templates/parametres/settings.html`
- Modify: `src/core/urls.py`, `src/templates/base.html`
- Test: `src/parametres/tests.py`

- [ ] **Step 1: Écrire les tests qui échouent**

Ajouter à `src/parametres/tests.py` (imports : `from django.contrib.auth import get_user_model`, `from django.urls import reverse`) :

```python
User = get_user_model()


class SettingsViewTests(TestCase):
    def setUp(self):
        self.url = reverse('settings_home')
        self.admin = User.objects.create_superuser(username='boss', password='pass12345')
        self.user = User.objects.create_user(username='simple', password='pass12345')

    def test_anonymous_is_redirected_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_non_admin_gets_403(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.assertEqual(self.client.post(self.url, company_data()).status_code, 403)

    def test_admin_sees_each_tab(self):
        self.client.force_login(self.admin)
        for tab in ('ctams', 'cta', 'documents'):
            response = self.client.get(self.url, {'onglet': tab})
            self.assertEqual(response.status_code, 200, tab)
        self.assertEqual(self.client.get(self.url, {'onglet': 'inconnu'}).status_code, 200)

    def test_admin_saves_company_tab(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            self.url + '?onglet=cta', company_data(rccm='CI-ABJ-2020-B-77', ncc='9999 Z'),
        )
        self.assertRedirects(response, self.url + '?onglet=cta')
        cta = CompanyProfile.objects.get(key='cta')
        self.assertEqual(cta.rccm, 'CI-ABJ-2020-B-77')
        self.assertEqual(CompanyProfile.objects.get(key='ctams').rccm, '')

    def test_invalid_company_form_is_not_saved(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url + '?onglet=cta', company_data(email='nope'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CompanyProfile.objects.get(key='cta').email, 'centretechniqueauto@outlook.com')

    def test_admin_saves_documents_tab(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            self.url + '?onglet=documents',
            {'tva_taux': '10', 'conditions_paiement': 'Comptant', 'penalites_retard': 'Aucune'},
        )
        self.assertRedirects(response, self.url + '?onglet=documents')
        defaults = DocumentDefaults.load()
        self.assertEqual(defaults.tva_taux, 10)
        self.assertEqual(defaults.conditions_paiement, 'Comptant')

    def test_menu_link_visible_for_admin(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, self.url)
```

- [ ] **Step 2: Lancer, vérifier l'échec**

Run: `cd src && ../venv/Scripts/python.exe manage.py test parametres.tests.SettingsViewTests`
Expected: `NoReverseMatch: 'settings_home' is not a registered namespace`.

- [ ] **Step 3: Écrire la vue et les routes**

`src/parametres/views.py` :

```python
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import CompanyProfileForm, DocumentDefaultsForm
from .models import CompanyProfile, DocumentDefaults

TABS = (
    ('ctams', 'CTAMS'),
    ('cta', 'CTA'),
    ('documents', 'Documents'),
)
TAB_KEYS = [key for key, _ in TABS]


@login_required(login_url='login')
@permission_required('users.manage_users', raise_exception=True)
@require_http_methods(['GET', 'POST'])
def settings_home(request):
    tab = request.GET.get('onglet', 'ctams')
    if tab not in TAB_KEYS:
        tab = 'ctams'

    if tab == 'documents':
        form_class, instance, profile = DocumentDefaultsForm, DocumentDefaults.load(), None
    else:
        profile = get_object_or_404(CompanyProfile, key=tab)
        form_class, instance = CompanyProfileForm, profile

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paramètres enregistrés.')
            return redirect(f"{reverse('settings_home')}?onglet={tab}")
    else:
        form = form_class(instance=instance)

    return render(request, 'parametres/settings.html', {
        'tabs': TABS,
        'tab': tab,
        'form': form,
        'profile': profile,
    })
```

`src/parametres/urls.py` :

```python
from django.urls import path

from . import views

urlpatterns = [
    path('', views.settings_home, name='settings_home'),
]
```

Dans `src/core/urls.py`, ajouter dans `urlpatterns`, après la ligne `factures/` : `    path('parametres/', include('parametres.urls')),`.

- [ ] **Step 4: Écrire la page**

`src/templates/parametres/settings.html` :

```html
{% extends 'base.html' %}
{% load static %}

{% block page_title %}Paramètres{% endblock %}
{% block topbar_title %}Paramètres{% endblock %}

{% block content %}

<div class="page-header">
  <div class="page-header-left">
    <h1 class="page-title">Paramètres</h1>
    <p class="page-subtitle">Informations des entreprises et valeurs par défaut des documents.</p>
  </div>
</div>

<div class="tab-nav">
  {% for key, label in tabs %}
    <a href="?onglet={{ key }}" class="tab-btn {% if key == tab %}active{% endif %}" style="text-decoration:none">{{ label }}</a>
  {% endfor %}
</div>

<div class="form-card">

  {% if form.non_field_errors %}
    <div class="form-error-banner mt-0" style="margin:20px 20px 0">
      <i class="fa-solid fa-triangle-exclamation"></i>
      {{ form.non_field_errors }}
    </div>
  {% endif %}

  <form method="post" action="?onglet={{ tab }}" enctype="multipart/form-data">
    {% csrf_token %}
    <div class="form-body">
      <div class="form-grid">
        {% for field in form %}
          {% if field.name == 'name' %}
            <h3 class="form-full" style="margin:0;font-size:.8rem;text-transform:uppercase;letter-spacing:.06em;color:var(--c-gray-500)">Identité</h3>
          {% elif field.name == 'rccm' %}
            <h3 class="form-full" style="margin:12px 0 0;font-size:.8rem;text-transform:uppercase;letter-spacing:.06em;color:var(--c-gray-500)">Informations légales</h3>
          {% elif field.name == 'bank_name' %}
            <h3 class="form-full" style="margin:12px 0 0;font-size:.8rem;text-transform:uppercase;letter-spacing:.06em;color:var(--c-gray-500)">Paiement</h3>
          {% elif field.name == 'logo' %}
            <h3 class="form-full" style="margin:12px 0 0;font-size:.8rem;text-transform:uppercase;letter-spacing:.06em;color:var(--c-gray-500)">Logo</h3>
          {% endif %}

          {% if field.name == 'logo' %}
            <div class="field form-full">
              <img src="{{ profile.logo_url }}" alt="Logo actuel" style="height:64px;width:auto;max-width:200px;object-fit:contain;border:1px solid var(--c-gray-200);border-radius:6px;padding:4px;margin-bottom:8px">
              <label for="{{ field.id_for_label }}">{{ field.label }} (JPG, PNG ou WEBP, 2 Mo max)</label>
              {{ field }}
              {% if field.errors %}<span class="field-error"><i class="fa-solid fa-circle-exclamation"></i> {{ field.errors|striptags }}</span>{% endif %}
            </div>
          {% elif field.name == 'remove_logo' %}
            <div class="field form-full">
              <label style="display:flex;align-items:center;gap:8px;font-weight:400">
                {{ field }} {{ field.label }}
              </label>
            </div>
          {% else %}
            <div class="field {% if field.name == 'full_name' or field.name == 'address' or field.name == 'conditions_paiement' or field.name == 'penalites_retard' %}form-full{% endif %}">
              <label for="{{ field.id_for_label }}">{{ field.label }}</label>
              {{ field }}
              {% if field.errors %}
                <span class="field-error"><i class="fa-solid fa-circle-exclamation"></i> {{ field.errors|striptags }}</span>
              {% endif %}
            </div>
          {% endif %}
        {% endfor %}
      </div>
    </div>

    <div class="form-actions">
      <button type="submit" class="btn btn-primary">
        <i class="fa-solid fa-floppy-disk"></i> Enregistrer
      </button>
    </div>
  </form>

</div>

{% endblock %}
```

- [ ] **Step 5: Ajouter le lien au menu**

Dans `src/templates/base.html`, dans le bloc `{% if user.is_staff or user.profile.role.code == 'admin' %}` de la section Administration, juste après le lien « Rôles » (avant `{% endif %}`), ajouter :

```html
      <a href="{% url 'settings_home' %}"
         class="sidebar-link {% if request.resolver_match.url_name == 'settings_home' %}active{% endif %}">
        <i class="fa-solid fa-gear"></i>
        <span>Paramètres</span>
      </a>
```

- [ ] **Step 6: Lancer, vérifier le succès**

Run: `cd src && ../venv/Scripts/python.exe manage.py test parametres invoices`
Expected: tous OK.

- [ ] **Step 7: Vérification visuelle**

Run: `cd src && ../venv/Scripts/python.exe manage.py runserver`, se connecter en admin, ouvrir `/parametres/`, vérifier : les 3 onglets, l'aperçu du logo, l'enregistrement du RCCM sur CTA, puis ouvrir l'impression d'une facture `?marque=cta` et constater le RCCM dans « Émetteur ». Vérifier aussi le mode sombre et la largeur mobile. Noter tout défaut de mise en page et corriger le HTML/CSS inline.

- [ ] **Step 8: Commit**

```bash
git add src/parametres src/templates/parametres src/templates/base.html src/core/urls.py
git commit -m "$(cat <<'EOF'
Page Paramètres : entreprises CTAMS/CTA et valeurs par défaut des documents

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: Pré-remplissage des nouveaux documents

**Files:**
- Modify: `src/invoices/views.py` (fonctions `invoice_create` et `proforma_create`)
- Test: `src/invoices/tests.py`

- [ ] **Step 1: Écrire les tests qui échouent**

Ajouter à `src/invoices/tests.py` (import : `from parametres.models import CompanyProfile, DocumentDefaults`) :

```python
class DocumentDefaultsPrefillTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='creator', password='pass12345')
        self.client.force_login(user)
        defaults = DocumentDefaults.load()
        defaults.tva_taux = 10
        defaults.conditions_paiement = 'Comptant'
        defaults.penalites_retard = 'Aucune'
        defaults.save()

    def test_new_invoice_form_uses_defaults(self):
        form = self.client.get(reverse('invoice_create')).context['form']
        self.assertEqual(form['tva_taux'].value(), 10)
        self.assertEqual(form['conditions_paiement'].value(), 'Comptant')
        self.assertEqual(form['penalites_retard'].value(), 'Aucune')

    def test_new_proforma_form_uses_default_tva(self):
        form = self.client.get(reverse('proforma_create')).context['form']
        self.assertEqual(form['tva_taux'].value(), 10)
```

- [ ] **Step 2: Lancer, vérifier l'échec**

Run: `cd src && ../venv/Scripts/python.exe manage.py test invoices.tests.DocumentDefaultsPrefillTests`
Expected: FAIL (`Decimal('18') != 10` et les anciens textes).

- [ ] **Step 3: Pré-remplir dans les vues**

Dans `src/invoices/views.py` :

- Ajouter l'import : `from parametres.models import DocumentDefaults`
- Dans `invoice_create`, remplacer `        form = InvoiceForm()` par :

```python
        defaults = DocumentDefaults.load()
        form = InvoiceForm(initial={
            'tva_taux': defaults.tva_taux,
            'conditions_paiement': defaults.conditions_paiement,
            'penalites_retard': defaults.penalites_retard,
        })
```

- Dans `proforma_create`, remplacer `        form = ProformaForm()` par :

```python
        form = ProformaForm(initial={'tva_taux': DocumentDefaults.load().tva_taux})
```

(Ne pas toucher aux vues d'édition.)

- [ ] **Step 4: Lancer toute la suite**

Run: `cd src && ../venv/Scripts/python.exe manage.py test`
Expected: tous les tests passent (customers, invoices, parametres, users, vehicles, workshop). Si un test hors périmètre échoue, vérifier avec `git stash` qu'il échouait déjà avant ; le signaler sans le corriger.

- [ ] **Step 5: Commit**

```bash
git add src/invoices/views.py src/invoices/tests.py
git commit -m "$(cat <<'EOF'
Nouvelles factures et proformas pré-remplies depuis les valeurs par défaut

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 7: Déploiement (confirmation de l'utilisateur requise avant ce task)

Ce task modifie un serveur partagé (autres projets djona). Ne l'exécuter qu'après accord explicite de l'utilisateur. Connexion : `ssh ctams_deploy`. Application : `/var/www/project/atelierProjet`, service `atelier` (port 8001), site `ctams.online`.

**Constats préalables (vérifiés le 2026-10-27) :**
- Pillow n'est pas installé sur le VPS (`ModuleNotFoundError: PIL`).
- `/etc/nginx/sites-enabled/app` n'a pas de bloc `location /media/`, et `src/media_cdn` appartient à `root` (755) : `www-data` ne peut pas y écrire.
- `client_max_body_size` est à 4M dans `nginx.conf` : suffisant pour des logos de 2 Mo.

- [ ] **Step 1: Pousser**

```bash
git push origin main
```

- [ ] **Step 2: Mettre à jour le code, les dépendances et la base**

```bash
ssh ctams_deploy 'cd /var/www/project/atelierProjet && git pull --ff-only origin main && venv/bin/pip install -r requirements.txt && cd src && ../venv/bin/python manage.py migrate && ../venv/bin/python manage.py collectstatic --noinput'
```

Expected : `Applying customers.0002_customer_rccm_ncc... OK`, `Applying parametres.0001_initial... OK`, `Applying parametres.0002_seed_defaults... OK`.

- [ ] **Step 3: Rendre le dossier des logos inscriptible**

```bash
ssh ctams_deploy 'chown -R www-data:www-data /var/www/project/atelierProjet/src/media_cdn'
```

- [ ] **Step 4: Servir `/media/` par nginx (avec sauvegarde et test)**

```bash
ssh ctams_deploy 'cp /etc/nginx/sites-available/app /root/app.nginx.bak.$(date +%s)'
```

Dans `/etc/nginx/sites-available/app`, dans le bloc `server` du port 443 (celui qui contient `location /static/`), juste après le bloc `location /static/ { ... }`, ajouter :

```nginx
location /media/ {

alias /var/www/project/atelierProjet/src/media_cdn/;

}
```

Puis :

```bash
ssh ctams_deploy 'nginx -t && systemctl reload nginx'
```

Expected : `syntax is ok` / `test is successful`. Si `nginx -t` échoue, restaurer la sauvegarde et ne pas recharger.

- [ ] **Step 5: Redémarrer et vérifier**

```bash
ssh ctams_deploy 'systemctl restart atelier && sleep 2 && systemctl is-active atelier && curl -s -o /dev/null -w "%{http_code}\n" https://ctams.online/parametres/'
```

Expected : `active` puis `302` (redirection vers la connexion). Ensuite, avec l'utilisateur : se connecter en admin sur `https://ctams.online/parametres/`, téléverser un logo de test sur CTA, ouvrir l'impression d'une facture `?marque=cta` et vérifier que le logo s'affiche (preuve que `/media/` est servi), puis remettre le logo par défaut.
