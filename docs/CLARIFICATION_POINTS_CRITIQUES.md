# Clarification des 5 Points Critiques - CTAMS

**Date**: 20 février 2026  
**Status**: À valider par le sponsor avant Phase 2  
**Audience**: PO, DG, Développeurs

---

## 1. Stack Technique Exact

### Django REST Framework & Architecture API

**Décision requise:**
- Approche A : **Django Templates + Forms** (plus simple, rapid dev)
  - Frontend : Django templates avec HTMX pour interactivité
  - Mobile V1 : PWA responsive simple
  - ✅ Plus rapide, moins de dépendances
  - ❌ Moins flexible pour mobile natif V2

- Approche B : **Django REST API + SPA légère** (scalable, évolutif)
  - Backend : API REST complète (DRF)
  - Frontend : Vue 3 ou React minimal
  - Mobile V1 : Même API + responsive web
  - ✅ Prêt pour mobile natif V2, découplage clean
  - ❌ Overhead dev initial +20%

**Recommandation Django senior** : **Approche B + DRF** pour CTAMS (complexité métier + évolution mobile V2)

### Stack détaillé proposé

```
Python 3.11 LTS
Django 4.2 LTS
Django REST Framework 3.14+
PostgreSQL 15+
Celery 5.3+ + Redis 7+
django-filter 23.3+
django-simple-history 3.4+
Pillow 10+
WeasyPrint 59+ (PDF, meilleur rendu que ReportLab)
python-jose 3.3+ (JWT tokens)
djangorestframework-simplejwt 5.3+
python-decouple 3.8+ (config env)
psycopg2-binary 2.9+ (PostgreSQL driver)
drf-spectacular 0.27+ (Doc API auto)
```

---

## 2. Gestion des Permissions et Rôles

### Stratégie RBAC (Role-Based Access Control)

**Décision requise:**

Approche A : **django-guardian** (granularité objet)
- Permissions par objet (devis 42 visible seulement par technicien X)
- ✅ Fine granularité
- ❌ Complexe, perf impact sur grandes listes

Approche B : **Custom RBAC + Decorators** (simple, performant)
- Groupes Django (DG, Assistante, Chef, Technicien, Compta)
- Permissions par vue/endpoint
- Filtrage données par groupe + user
- ✅ + Rapide, maintenable
- ✅ Suffisant pour CTAMS V1

**Recommandation** : **Approche B + implémentation custom**

### Rôles et Permissions définis

```python
ROLES = {
    'DG': {
        'perms': ['dashboard_full', 'export_all', 'settings', 'user_mgmt'],
        'visible': 'Tous les devis/factures/interventions'
    },
    'Assistante': {
        'perms': ['create_client', 'create_quote', 'create_invoice', 'receive_payment'],
        'visible': 'Clients/devis/factures assignés ou globaux'
    },
    'Chef_Service': {
        'perms': ['plan_intervention', 'assign_technician', 'validate_quality'],
        'visible': 'Interventions de son service uniquement'
    },
    'Technicien': {
        'perms': ['view_assigned_tasks', 'update_progress', 'checklist'],
        'visible': 'Ses propres tâches assignées'
    },
    'Comptabilite': {
        'perms': ['view_invoices', 'report_payments', 'export_accounting'],
        'visible': 'Factures et paiements seulement'
    }
}
```

---

## 3. Numérotation Devis & Factures

### Stratégie d'unicité atomique

**Décision requise:**

Approche A : **Séquence PostgreSQL + trigger DB**
- Format: `DV-2026-{numéro séquentiel}`
- Ex: `DV-2026-001`, `DV-2026-002`
- ✅ Garantie atomicité DB
- ✅ Pas de collision même si 10000 créations/sec
- ❌ Dépendance DB

Approche B : **Model Django + transaction.atomic()**
```python
with transaction.atomic():
    last = Quote.objects.select_for_update().latest('quote_number')
    new_num = last.quote_number + 1
    quote = Quote.objects.create(quote_number=new_num, ...)
```
- ✅ Portable DB-agnostic
- ⚠️ Moins rapide sous forte charge

**Recommandation** : **Approche A (séquence PostgreSQL)** pour robustesse

### Implémentation

```python
# models.py
class Quote(models.Model):
    quote_number = models.IntegerField(unique=True, db_index=True)
    quote_ref = models.CharField(max_length=20, unique=True)  # 'DV-2026-001'
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.quote_number:
            self.quote_number = self._get_next_quote_number()
        if not self.quote_ref:
            self.quote_ref = f"DV-{self.created_at.year}-{self.quote_number:06d}"
        super().save(*args, **kwargs)
    
    @staticmethod
    def _get_next_quote_number():
        with connection.cursor() as cursor:
            cursor.execute("SELECT nextval('quote_seq')")
            return cursor.fetchone()[0]
```

---

## 4. Signature Numérique & PDF

### Mécanisme de signature retenu

**Décision requise:**

Approche A : **Signature simple par email** (MVP)
- Client reçoit lien emailavec token signé
- Clique "J'accepte" = validation enregistrée
- Stocker : utilisateur, timestamp, IP
- ✅ Rapide MVP
- ❌ Vaut pas signature légale en France

Approche B : **Signature avancée (certificat DigiCert/Docusign API)**
- Valeur légale auprès des autorités FR
- ✅ Conforme factures
- ❌ Coûteux ($ par signature), latence API

**Recommandation V1** : **Approche A (email validation)** + **migration simple vers B en V2**

### PDF Generation

**Décision requise:**

- **WeasyPrint** (recommandé) : HTML→PDF, rendu excellent, design flexible
- **ReportLab** : programmatique, plus lourd
- **xhtml2pdf** : deprecated

**Recommandation** : **WeasyPrint** + stockage PDF en media/invoices/

### Architecture

```python
# services/quote_service.py
class QuotePDFGenerator:
    @staticmethod
    def generate_pdf(quote: Quote) -> bytes:
        """Génère PDF depuis template Django"""
        html_string = render_to_string('quotes/quote_template.html', {'quote': quote})
        pdf_bytes = HTML(string=html_string).write_pdf()
        quote.pdf_file.save(f'quote_{quote.quote_ref}.pdf', 
                           ContentFile(pdf_bytes))
        return pdf_bytes

class QuoteSignatureService:
    @staticmethod
    def send_for_signature(quote: Quote, client_email: str):
        """Envoie lien signature au client"""
        token = signing.dumps({'quote_id': quote.id}, key=settings.SECRET_KEY)
        link = f"{settings.FRONTEND_URL}/sign-quote/{token}"
        send_email_async.delay(
            to=client_email,
            subject=f"Devis {quote.quote_ref} à signer",
            template='email/signature_request.html',
            context={'quote': quote, 'link': link}
        )
    
    @staticmethod
    def validate_signature(token: str):
        """Valide signature et crée SignatureLog"""
        try:
            data = signing.loads(token, max_age=604800)  # 7 jours
            quote = Quote.objects.get(id=data['quote_id'])
            QuoteSignature.objects.create(
                quote=quote,
                signed_by=request.user,
                signed_at=now(),
                ip_address=get_client_ip(request)
            )
            quote.status = 'signed'
            quote.save()
            return True
        except Exception as e:
            logger.error(f"Signature validation failed: {e}")
            return False
```

---

## 5. Audit Logs & Traçabilité

### Stratégie logging

**Décision requise:**

Approche A : **django-simple-history** (plug & play)
```python
class Quote(models.Model):
    history = HistoricalRecords()
    # Retrouve auto: CRUD + who/when
```
- ✅ Automatique, simple
- ✅ Révisions faciles
- ❌ Stockage 3x volume DB

Approche B : **Custom AuditLog model**
```python
class AuditLog(models.Model):
    entity_type = models.CharField()  # 'Quote', 'Invoice'
    entity_id = models.IntegerField()
    action = models.CharField()  # 'CREATE', 'UPDATE', 'DELETE'
    changed_fields = models.JSONField()
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField()
```
- ✅ Contrôle total
- ✅ Léger
- ❌ À implémenter

**Recommandation** : **Approche A (django-simple-history)** pour robustesse

### Implémentation avec signaux Django

```python
# models.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Quote)
def log_quote_change(sender, instance, created, **kwargs):
    action = 'CREATE' if created else 'UPDATE'
    AuditLog.objects.create(
        entity_type='Quote',
        entity_id=instance.id,
        action=action,
        created_by=instance.created_by,
        timestamp=now()
    )

@receiver(post_delete, sender=Quote)
def log_quote_delete(sender, instance, **kwargs):
    AuditLog.objects.create(
        entity_type='Quote',
        entity_id=instance.id,
        action='DELETE',
        created_by=instance.last_modified_by,
        timestamp=now()
    )
```

---

## Résumé Décisions

| Point | Recommandation | Validation |
|-------|-----------------|-----------|
| **API Architecture** | DRF REST API | ☐ PO |
| **Permissions** | Custom RBAC + Decorators | ☐ DG |
| **Numérotation** | PostgreSQL Sequence | ☐ Compta |
| **Signature** | Email validation + WeasyPrint PDF | ☐ DG |
| **Audit** | django-simple-history | ☐ Audit |

---

## Prochaines Étapes

1. **Valider** ce document avec sponsor (24h max)
2. **Créer requirements.txt** avec dépendances finalisées
3. **Fixer venv** et PostigreSQL
4. **Démarrer Phase 2** : Structure apps + modèles de base
