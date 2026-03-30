# Instructions de realisation pas a pas - Projet CTAMS (Django)

Ce document decrit l'ordre d'execution recommande pour realiser le projet a partir de la base Django existante (`src/`), en s'appuyant sur `cahier_des_charges_ctams.md`.

## 1. Cadrage initial (obligatoire avant dev fonctionnel)

1. Valider le scope V1 :
- Modules inclus : clients, vehicules, devis, factures/paiements, atelier, dashboard DG.
- Mobile V1 : PWA responsive (pas de natif en V1).

2. Figer les regles metier critiques :
- Regle de numerotation devis/facture.
- Taux TVA et exceptions.
- Liste finale des statuts (devis, facture, intervention).
- Regles de blocage qualite avant restitution.

3. Produire les artefacts de cadrage :
- Diagramme des flux metier.
- Dictionnaire de donnees (champ, type, obligatoire, validation).
- Matrice role -> permissions.

Livrable :
- Dossier `docs/cadrage/` avec ces 3 documents.

## 2. Preparation technique du socle

1. Structurer le projet en apps metier (dans `src/`) :
- `customers`
- `vehicles`
- `quotes`
- `invoices`
- `workshop`
- `reporting`
- `audit`

2. Mettre a jour `src/core/settings.py` :
- Ajouter les apps dans `INSTALLED_APPS`.
- Configurer timezone, locale, format date.
- Configurer DRF (si API exposee en V1).

3. Mettre a jour `src/core/urls.py` :
- Declarer les routes par module (namespaces).

4. Mettre en place une base de permissions :
- Groupes Django : DG, Assistante, ChefService, Technicien, Comptabilite.
- Decorateurs/mixins de controle d'acces.

Livrable :
- Projet demarrant avec routes modulees et roles de base.

## 3. Modele de donnees (migrations V1)

1. Implementer les modeles dans cet ordre :
- Clients/entreprises.
- Vehicules + liaison proprietaire.
- Devis + lignes + statuts + signature.
- Factures + lignes + paiements.
- Ordres de reparation + taches + check-list qualite.
- Journal d'audit.

2. Contraintes obligatoires :
- Immatriculation unique.
- Numeros devis/facture uniques et indexes.
- Integrite referentielle (FK + `on_delete` adapte).
- Champs `created_at`, `updated_at`, `created_by` sur entites sensibles.

3. Generer et appliquer les migrations :
- `python src/manage.py makemigrations`
- `python src/manage.py migrate`

Livrable :
- Schema V1 migre et stable.

## 4. Module Clients + Vehicules

1. Ecrans/formulaires :
- Creation client particulier.
- Creation client entreprise.
- Creation/edition vehicule.

2. Fonctionnalites :
- Recherche client (nom, telephone, immatriculation).
- Historique par client et par vehicule.
- Validation stricte des champs obligatoires.

3. Tests minimum :
- Tests modeles.
- Tests permissions (qui peut creer/modifier).
- Tests vues (creation/recherche).

Livrable :
- Parcours complet accueil -> creation client/vehicule operationnel.

## 5. Module Devis

1. Ecrans/formulaires :
- Creation devis avec lignes dynamiques.
- Resume financier auto-calcule (HT/TVA/TTC).

2. Regles metier :
- Numero auto-genere a la creation.
- Workflow statut : brouillon -> envoye -> signe/refuse -> valide.
- Un devis valide ne doit plus etre modifiable (hors regle explicite).

3. Sorties :
- PDF devis.
- Impression.
- Signature client (capture ou validation numerique).

4. Tests minimum :
- Exactitude calculs financiers.
- Transitions de statuts autorisees/interdites.

Livrable :
- Devis complet de bout en bout, avec PDF et statut.

## 6. Module Factures + Paiements

1. Generation facture :
- Creee uniquement depuis devis valide.
- Reprise des lignes et montants avec trace de conversion.

2. Paiements :
- Paiement partiel et total.
- Calcul du reste a payer.
- Historique des reglements.

3. Statuts facture :
- Emise, partiellement reglee, reglee, en retard, annulee.

4. Documents :
- PDF facture conforme (mentions legales).

5. Tests minimum :
- Conversion devis -> facture sans ecart.
- Changement de statut selon paiements.

Livrable :
- Chaine commerciale complete devis -> facture -> encaissement.

## 7. Module Atelier

1. Planification :
- Planning par service (Mecanique, Electricite, Tolerie, Climatisation).
- Affectation technicien par chef de service.

2. Execution :
- Ordre de reparation lie au devis/facture.
- Suivi statut intervention (a faire/en cours/en pause/termine).

3. Controle qualite :
- Check-list obligatoire.
- Blocage restitution tant que check-list non validee.

4. Tests minimum :
- Verification blocage qualite.
- Verification des permissions chef/technicien.

Livrable :
- Processus atelier pilotable et tracable.

## 8. Module Dashboard DG

1. KPI a implementer :
- Temps moyen de prise en charge.
- Taux satisfaction.
- Devis valides vs refuses.
- Rentabilite par service.
- Clients nouveaux vs recurrents.
- Recettes mensuelles.

2. Ecrans :
- Graphiques.
- Filtres (periode, service, technicien).
- Exports CSV/PDF.

3. Alertes :
- Seuil satisfaction < 80%.
- Option alertes factures en retard.

Livrable :
- Tableau de bord exploitable par DG.

## 9. Securite, audit, qualite

1. Securite :
- Verifier tous les acces par role.
- Protections CSRF et validations server-side.

2. Audit :
- Tracer creation/modification/validation/suppression.
- Afficher auteur + horodatage.

3. Qualite :
- Couverture tests sur modules critiques.
- Revue de code avant fusion.

Livrable :
- Application securisee et auditable.

## 10. Deploiement et exploitation

1. Environnements :
- `dev`, `preprod`, `prod`.

2. Configuration :
- Variables d'environnement.
- Base PostgreSQL.
- Stockage media/documents.

3. Operations :
- Sauvegarde quotidienne base + fichiers.
- Procedure de restauration testee.
- Journalisation erreurs.

Livrable :
- Procedure de mise en production et runbook.

## 11. Plan de livraison recommande (sprints)

1. Sprint 1 :
- Cadrage, modeles clients/vehicules, auth/roles.

2. Sprint 2 :
- Devis + PDF + statuts.

3. Sprint 3 :
- Factures + paiements + conformite.

4. Sprint 4 :
- Atelier + check-list qualite.

5. Sprint 5 :
- Dashboard DG + exports + alertes.

6. Sprint 6 :
- Durcissement securite, recette finale, formation.

## 12. Definition of Done (DoD) globale

Un module est termine si :
- Les cas fonctionnels nominaux + erreurs sont couverts.
- Les droits d'acces sont verifies.
- Les tests passent.
- Les migrations sont stables.
- La documentation utilisateur et technique est mise a jour.
- La recette metier est validee.

