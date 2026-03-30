# Cahier des charges - CTAMS (Outil de Gestion Atelier Mecanique Auto)

## 1. Analyse du brief technique

Le brief couvre bien les modules metier principaux (clients, devis, factures, atelier, dashboard DG), mais il manque des precisisons critiques pour garantir un projet Django robuste et exploitable en production.

Points a cadrer explicitement :
- Roles et permissions fines par profil.
- Workflow de statuts (devis, ordre de reparation, facture, paiement).
- Regles legales de facturation (numerotation, TVA, avoirs, archivage).
- Perimetre mobile (responsive/PWA vs application native).
- Exigences non fonctionnelles (performance, sauvegarde, securite, audit).
- Integrations externes (signature, email/SMS, export comptable).

## 2. Objectif du projet

Construire une plateforme CTAMS web + mobile pour gerer :
- Clients particuliers et entreprises.
- Parc vehicules.
- Devis et signatures clients.
- Factures et paiements.
- Planification et execution atelier.
- Pilotage DG par KPI.

Le systeme doit garantir la tracabilite complete, la conformite legale et une exploitation simple par tous les profils metier.

## 3. Perimetre fonctionnel

### 3.1 Gestion clients

Client particulier :
- Nom, prenom.
- Telephone, email.
- Adresse.
- Vehicule(s) : marque, modele, annee, immatriculation, kilometrage.
- Date et heure d'arrivee.

Client entreprise :
- Raison sociale.
- Contact principal.
- Telephone, email, adresse.
- Flotte de vehicules.
- Conditions commerciales specifiques (tarifs, contrat cadre).

Fonctions :
- Historique interventions/devis/factures/paiements par client.
- Historique par vehicule.
- Alertes d'entretien preventif (date/kilometrage).

### 3.2 Gestion vehicules

- Fiche vehicule unique par immatriculation.
- Liaison proprietaire (particulier ou entreprise).
- Historique pannes et interventions.
- Suivi kilometrage et pieces remplacees.

### 3.3 Devis

Champs/fonctions :
- Coordonnees client auto-remplies.
- Numero et date auto-generes.
- Lignes dynamiques (pieces, main-d'oeuvre, prix unitaire, quantite).
- Calcul automatique HT, TVA, TTC.
- Signature numerique client.
- Export PDF et impression.
- Conversion en facture.

Statuts :
- Brouillon, envoye, signe, refuse, expire, valide.

### 3.4 Facturation et paiements

Champs/fonctions :
- Generation depuis devis valide.
- Mentions legales obligatoires.
- Numero et date auto-generes.
- Mode de paiement, date de reglement, reference.
- Historique des paiements.
- Export PDF et impression.

Statuts facture :
- Emise, partiellement reglee, reglee, en retard, annulee.

### 3.5 Atelier / services techniques

Services :
- Mecanique, Electricite, Tolerie, Climatisation.

Fonctions :
- Planning interventions par service.
- Affectation techniciens par chef de service.
- Suivi d'avancement temps reel.
- Controle qualite via check-list avant restitution.
- Liaison ordre de reparation <-> devis <-> facture.

Statuts intervention :
- A faire, en cours, en pause, termine, controle qualite valide.

### 3.6 Tableau de bord DG

KPI :
- Temps moyen de prise en charge.
- Taux de satisfaction client.
- Devis valides vs refuses.
- Rentabilite par service.
- Fidelisation (nouveaux vs recurrents).
- Recettes mensuelles.

Fonctions :
- Graphiques interactifs.
- Filtres par periode, service, technicien.
- Exports CSV/PDF.
- Alertes automatiques sur seuils (ex: satisfaction < 80%).

## 4. Roles et habilitations

- DG : acces global, KPI, exports globaux, parametres.
- Assistante/Accueil : creation clients/vehicules, devis/factures, encaissements.
- Chef de service : planning, affectation, validation qualite.
- Technicien : consultation taches assignees, mise a jour avancement, check-list.
- Comptabilite (option) : supervision paiements, exports financiers.

Exigence :
- Journal d'audit obligatoire pour toute action sensible (creation/modification/validation/suppression).

## 5. Exigences non fonctionnelles

### 5.1 Architecture technique

- Backend : Django + Django REST Framework.
- Base de donnees : PostgreSQL.
- Frontend : Django templates (ou SPA legere selon budget).
- Mobile V1 : PWA responsive.
- Mobile V2 : application native (option evolutive).

### 5.2 Securite

- Authentification securisee.
- Gestion des droits par role (RBAC).
- Protection CSRF.
- Hash des mots de passe.
- Chiffrement TLS en production.
- Audit log horodate.
- Sauvegardes quotidiennes automatiques.

### 5.3 Performance et exploitation

- Temps de reponse cible : < 2 secondes sur 95% des ecrans metier.
- Pagination obligatoire sur listes volumineuses.
- Disponibilite cible : 99.5% (hors maintenance planifiee).
- Monitoring applicatif et alertes techniques.

### 5.4 Conformite

- Respect RGPD : minimisation des donnees, droits d'acces/suppression, journalisation.
- Conservation legale des documents de facturation selon reglementation applicable.

## 6. Modele de donnees cible (noyau)

Entites principales :
- User, Role, Permission.
- Client, CompanyProfile.
- Vehicle, VehicleOwnership.
- WorkOrder, WorkTask, ServiceDepartment.
- Quote, QuoteLine, QuoteSignature.
- Invoice, InvoiceLine.
- Payment, PaymentMethod.
- MaintenanceReminder.
- QualityChecklist, ChecklistItem, ChecklistResult.
- ReportingSnapshot/KPIEvent.
- AuditLog.
- Document (PDF de devis/factures/rapports).

## 7. Workflows metier critiques

### 7.1 Parcours principal

1. Accueil vehicule -> creation/mise a jour client + vehicule.
2. Diagnostic initial -> creation devis.
3. Signature/validation devis -> creation ordre de reparation.
4. Affectation atelier -> execution intervention.
5. Controle qualite valide -> restitution.
6. Generation facture -> encaissement partiel/total -> cloture dossier.

### 7.2 Automatismes

- Rappel entretien preventif.
- Relance factures impayees.
- Alertes KPI hors seuil.
- Historisation automatique des changements de statut.

## 8. API et integrations

- API REST securisee pour mobile/PWA.
- Generation PDF serveur.
- Module de signature numerique (interne ou tiers).
- Envoi email/SMS (notifications client et relances).
- Exports comptables CSV.

## 9. Strategie de test et recette

### 9.1 Tests techniques

- Tests unitaires (regles metier, calculs HT/TVA/TTC).
- Tests d'integration API.
- Tests de non-regression sur workflows critiques.
- Tests de droits par role.

### 9.2 Recette metier (criteres d'acceptation)

- Champs obligatoires controles partout.
- Numerotation devis/factures unique, sans collision.
- Conversion devis -> facture sans perte ni alteration de donnees.
- Factures et paiements geres correctement (partiel/total).
- Check-list qualite bloquante avant restitution.
- KPI coherents avec donnees operationnelles.

## 10. Plan de realisation (estimation 12 semaines)

1. S1-S2 : cadrage detaille, ateliers metier, maquettes ecrans.
2. S3 : socle technique, auth, roles/permissions.
3. S4-S5 : clients, entreprises, vehicules, historique.
4. S6-S7 : devis, signature, PDF, workflow validation.
5. S8 : factures, paiements, relances.
6. S9-S10 : atelier, planning, affectation, check-list qualite.
7. S11 : dashboard DG, KPI, exports, alertes.
8. S12 : recette finale, formation, deploiement initial.

## 11. Livrables

- Application CTAMS operationnelle (web + PWA mobile).
- Documentation technique (architecture, installation, exploitation).
- Manuel utilisateur par role (DG, assistante, chef, technicien, accueil).
- Jeu de tests automatises et rapport de couverture.
- Scripts de migration et de sauvegarde/restauration.
- Plan de formation personnel.
- Plan de support/maintenance (corrective et evolutive).

## 12. Points de validation avec le sponsor (avant demarrage dev)

- Choix definitif du perimetre mobile (PWA seule ou natif cible).
- Regles de numerotation comptable/facturation.
- Taux TVA et cas particuliers.
- Niveau de details du controle qualite atelier.
- Mecanisme de signature retenu.
- Canaux de notification (email, SMS, WhatsApp si necessaire).
- SLA support et niveau de maintenance attendus.
