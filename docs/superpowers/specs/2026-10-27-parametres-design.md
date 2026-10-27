# Page Paramètres — design

Date : 2026-10-27

## Objectif

Une page « Paramètres » réservée aux administrateurs, pour modifier sans toucher au code :
l'identité de chaque entreprise (CTAMS, CTA), ses numéros légaux (RCCM, NCC), ses coordonnées de
paiement, son logo, et les valeurs par défaut des documents (TVA, conditions, pénalités).

Aujourd'hui ces informations sont écrites en dur dans `src/invoices/branding.py`.

## Hors périmètre

- Pas de réglages par utilisateur (thème, langue).
- Pas de gestion de plus de deux entreprises dans l'interface (le modèle le permet, l'écran non).
- Pas de changement de la logique « marque choisie à l'impression » (`?marque=ctams|cta`).

## Données

Nouvelle app Django `parametres` (`src/parametres/`), ajoutée à `LOCAL_APPS`.

### `CompanyProfile` — une ligne par entreprise

| Champ | Type | Note |
|---|---|---|
| `key` | slug, unique | `ctams` ou `cta`, clé utilisée par `?marque=` |
| `name` | char 80 | « CTAMS » |
| `tag` | char 150, vide autorisé | slogan sous le nom |
| `full_name` | char 200 | nom complet de l'émetteur |
| `address` | char 255 | |
| `tel` | char 100 | un ou plusieurs numéros |
| `email` | email | |
| `signataire` | char 150, vide autorisé | texte sous la signature |
| `rccm` | char 100, vide autorisé | |
| `ncc` | char 100, vide autorisé | |
| `bank_name` | char 100, vide autorisé | |
| `bank_account` | char 100, vide autorisé | IBAN / RIB |
| `mobile_money` | char 150, vide autorisé | ex. « Wave 07 77 90 68 45 » |
| `logo` | image, vide autorisé | téléversée dans `media_cdn/` |

Historique des modifications via `simple_history` (`HistoricalRecords`), déjà installé.

### `DocumentDefaults` — une seule ligne

`tva_taux` (décimal, défaut 18), `conditions_paiement` (texte), `penalites_retard` (texte).

### Données initiales

Une migration de données crée :
- les deux `CompanyProfile` avec exactement les valeurs actuelles de `branding.py` ;
- la ligne `DocumentDefaults` avec TVA 18 % et les conditions de paiement / pénalités actuelles du modèle `Invoice`.

Tant que personne ne modifie rien, les documents imprimés sont identiques à aujourd'hui.

## Branchement sur l'existant

- `get_brand(request)` (dans `invoices/branding.py`) lit `CompanyProfile` selon `?marque=`.
  Il renvoie le même dictionnaire qu'aujourd'hui (`key, logo, name, tag, full_name, address, tel,
  email, signataire`) plus `rccm, ncc, bank_name, bank_account, mobile_money, logo_url`.
  Clé inconnue ou absente : CTAMS. Si la base n'a pas la ligne : repli sur les valeurs en dur
  conservées dans le module, pour qu'une base vide ne casse pas l'impression.
- Logo : si `logo` est renseigné on utilise son URL, sinon le fichier statique actuel
  (`app/assets/img/ctams-logo.jpg` / `cta-logo.png`). Les trois modèles d'impression passent de
  `{% static brand.logo %}` à une valeur unique `brand.logo_url`.
- Modèles d'impression (`invoice_print`, `proforma_print`, `delivery_print`) : dans le bloc
  « Émetteur », afficher RCCM et NCC, puis banque / compte / Mobile Money, chacun seulement s'il est
  renseigné. Les champs Tél et Email modifiables avant impression restent, initialisés avec les
  valeurs des réglages.
- Création d'une facture : `tva_taux`, `conditions_paiement` et `penalites_retard` sont pré-remplis
  depuis `DocumentDefaults`. Création d'un proforma : seulement `tva_taux` (le proforma n'a pas de
  conditions). L'édition d'un document existant ne change rien.

## Interface

- Lien « Paramètres » (icône engrenage) dans la section « Administration » du menu de
  `templates/base.html`, avec la même condition d'affichage que Utilisateurs et Rôles
  (`user.is_staff or user.profile.role.code == 'admin'`).
- Route `/parametres/` (nom `settings_home`), onglet choisi par `?onglet=ctams|cta|documents`.
- Trois onglets, chacun avec son propre formulaire et son bouton Enregistrer :
  **CTAMS**, **CTA**, **Documents**. Même mise en page que `customers/form.html`
  (`form-card`, `form-grid`, `field`).
- Le logo : aperçu du logo actuel, champ de téléversement, case « revenir au logo par défaut ».
- Message de confirmation après enregistrement (`django.contrib.messages`), retour sur le même onglet.

## Accès et validation

- La vue exige la connexion et le rôle admin ; un autre utilisateur reçoit une erreur 403.
  Même règle que la section Administration du menu.
- Validation par formulaire Django : email valide, logo limité aux images (JPG, PNG, WEBP) et à 2 Mo,
  `tva_taux` entre 0 et 100.
- Nom, nom complet, adresse, téléphone et email sont obligatoires pour une entreprise ; RCCM, NCC et
  paiement sont facultatifs.

## Tests

- Un non-admin reçoit 403 sur `/parametres/`, un admin reçoit 200.
- Après enregistrement d'un onglet, `get_brand` renvoie les nouvelles valeurs, y compris RCCM / NCC.
- Logo téléversé → `logo_url` pointe vers le média ; sans logo → fichier statique par défaut.
- La migration crée bien les deux entreprises et les valeurs par défaut, identiques à l'ancien
  `branding.py`.
- Création d'une facture : le formulaire est pré-rempli avec `DocumentDefaults`.
- Les pages d'impression affichent RCCM / NCC / paiement quand ils sont renseignés, et rien quand ils
  sont vides.

## Déploiement

`git pull`, `python manage.py migrate`, redémarrage du service `atelier`. Le dossier `media_cdn/`
doit être inscriptible par `www-data` pour les logos ; à vérifier sur le VPS et à servir par nginx
sous `/media/`.
