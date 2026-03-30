# 📦 Installation Complète - CTAMS Phase 2

**Date**: 20 février 2026  
**Status**: ✅ TERMINÉ  
**Python Version**: 3.13.3  
**Django Version**: 6.0.2

---

## 1. ✅ Environnement Python & Packages

### Packages clés installés (dernières versions)

```
Django                     6.0.2
djangorestframework        3.16.1
django-filter              25.2
django-cors-headers        4.9.0
django-simple-history      3.11.0
djangorestframework-simplejwt 5.5.1
drf-spectacular            0.29.0
celery                     5.6.2
redis                      7.2.0
psycopg2-binary            2.9.11
WeasyPrint                 68.1 ✨ (PDF Generation)
Pillow                     12.1.1
gunicorn                   25.1.0
whitenoise                 6.11.0
pytest                     9.0.2
pytest-django              4.12.0
black                      26.1.0
flake8                     7.3.0
```

**Total**: 45 packages (core + dev + testing)

---

## 2. ✅ Apps Django Créées

```
src/
├── customers/          ← Gestion clients (particuliers + entreprises)
├── vehicles/           ← Gestion parc véhicules
├── quotes/             ← Devis + énumération
├── invoices/           ← Factures + paiements
├── workshop/           ← Planning + interventions atelier
├── reporting/          ← Dashboard + KPI DG
├── audit/              ← Journal d'audit
└── users/              ← (existante) Auth + permissions
```

---

## 3. ✅ Configuration Django (settings.py)

### Améliorations apportées

#### ✓ Imports & Variables d'environnement
- Ajout `python-decouple` pour config via `.env`
- Support multilingue FR + timezone Europe/Paris
- Format dates : `d/m/Y H:i`

#### ✓ Apps Django
- Tous les modules métier + packages tiers
- `django-simple-history` pour audit automatique
- `drf-spectacular` pour doc API auto

#### ✓ REST Framework (DRF)
```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,  # 25 lignes par défaut
    'DEFAULT_FILTER_BACKENDS': ['DjangoFilterBackend', 'OrderingFilter', 'SearchFilter'],
    'DEFAULT_AUTHENTICATION_CLASSES': ['JWTAuthentication', 'SessionAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': ['IsAuthenticated'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',  # Doc Swagger
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

#### ✓ Database
- **Dev** : SQLite3 (par défaut)
- **Prod** : PostgreSQL via `.env` (`USE_POSTGRES=True`)
- Support variables d'env : `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

#### ✓ JWT Tokens
- Access duration: 1h
- Refresh duration: 7 jours
- Signing algorithm: HS256

#### ✓ CORS
- Origins configurables via `.env`
- Par défaut : `localhost:3000`, `localhost:5173` (Vue/React devs)

#### ✓ Static Files
- WhiteNoise middleware (compression + gestion production)
- `STATIC_ROOT` : `static_cdn/`
- `MEDIA_ROOT` : `media_cdn/`

#### ✓ Logging
- Console + fichier `logs/django.log`
- Format verbeux (timestamp, module, niveau)

---

## 4. ✅ Migrations Initiales

```bash
$ python manage.py migrate
Operations to perform:
  - contenttypes.0001_initial ✓
  - auth.0001-0012 ✓
  - admin.0001-0003 ✓
  - sessions.0001_initial ✓
```

**Database**: `db.sqlite3` créée ✓

---

## 5. ✅ Fichier `.env`

Créé avec variables de base :

```env
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
USE_POSTGRES=False
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8000
```

**À mise à jour avant production** ⚠️

---

## 6. ✅ Répertoires Créés

```
src/
├── logs/              ← Logs Django
```

---

## 7. 📋 Requirements.txt

Mis à jour avec versions flexibles (≥ au lieu de ==) pour faciliter MaJ futures.

**Localisation** : `/atelierProjet/requirements.txt`

---

## 🚀 Prochaines Étapes (Phase 3: Modèles de Données)

### A. Créer les modèles de base

```
1. users/models.py
   - CustomUser + roles (DG, Assistante, Chef, Technicien, Compta)
   - Permissions granulaires

2. customers/models.py
   - Client (particulier)
   - Company (entreprise)
   - Contact (liaisons)

3. vehicles/models.py
   - Vehicle
   - VehicleOwnership
   - MaintenanceHistory

4. quotes/models.py
   - Quote
   - QuoteLine
   - QuoteSignature (audit signature)

5. invoices/models.py
   - Invoice
   - InvoiceLine
   - Payment
   - PaymentMethod

6. workshop/models.py
   - ServiceDepartment
   - WorkOrder
   - WorkTask
   - QualityChecklist / ChecklistItem

7. audit/models.py
   - AuditLog (custom si pas django-simple-history)
```

### B. Validator les modèles

```bash
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py check
```

### C. Créer les serializers DRF

Pour chaque app : `serializers.py`

---

## ✅ Status Récapitulatif

| Item | Status | Notes |
|------|--------|-------|
| **Venv** | ✅ | Python 3.13.3 |
| **Packages** | ✅ | 45 packages, versions latest |
| **Apps** | ✅ | 8 apps Django créés |
| **Settings** | ✅ | Config DRF complète |
| **Database** | ✅ | SQLite ready |
| **Migrations** | ✅ | Django core tables initialized |
| **Env** | ✅ | .env present |
| **Ready for dev** | ✅ | Phase 3 peut démarrer |

---

## 🔧 Commandes Utiles

```bash
# Vérifier configuration
python manage.py check

# Faire migrations
python manage.py makemigrations
python manage.py migrate

# Créer admin
python manage.py createsuperuser

# Lancer dev server
python manage.py runserver 0.0.0.0:8000

# Installer packages supplémentaires
pip install <package_name>

# Générer doc API (Swagger)
python manage.py spectacular_settings --out schema.yml
```

---

## 📝 Notes

- **IDE**: VS Code + Python extension
- **Terminal**: Bash/Git Bash (Windows)
- **Version Control**: Git (via GitHub)
- **Production Ready**: À configurer dans Sprint 6

---

**Prêt pour Phase 3!** 🎯
