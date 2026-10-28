from django import forms
from .models import DeliveryNote, Invoice, InvoiceStatus, Proforma, ProformaStatus


class ProformaForm(forms.ModelForm):
    class Meta:
        model = Proforma
        fields = [
            'customer',
            'destinataire_nom', 'destinataire_adresse', 'destinataire_tel',
            'destinataire_email', 'destinataire_rccm', 'destinataire_ncc',
            'vehicule_marque', 'vehicule_modele', 'vehicule_immatriculation', 'vehicule_kilometrage',
            'date_emission',
            'reference_client', 'objet', 'bon_de_livraison',
            'remise_globale', 'tva_taux', 'status',
        ]
        widgets = {
            'date_emission': forms.DateInput(attrs={'type': 'date'}),
        }


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'customer',
            'destinataire_nom', 'destinataire_adresse', 'destinataire_tel',
            'destinataire_email', 'destinataire_rccm', 'destinataire_ncc',
            'vehicule_marque', 'vehicule_modele', 'vehicule_immatriculation', 'vehicule_kilometrage',
            'date_emission', 'date_echeance',
            'reference_client', 'objet', 'bon_de_livraison',
            'remise_globale', 'tva_taux', 'acompte_verse',
            'conditions_paiement', 'penalites_retard', 'status',
        ]
        widgets = {
            'date_emission': forms.DateInput(attrs={'type': 'date'}),
            'date_echeance': forms.DateInput(attrs={'type': 'date'}),
            'conditions_paiement': forms.Textarea(attrs={'rows': 2}),
            'penalites_retard': forms.Textarea(attrs={'rows': 2}),
        }


class DeliveryNoteForm(forms.ModelForm):
    class Meta:
        model = DeliveryNote
        fields = [
            'customer', 'invoice',
            'destinataire_nom', 'destinataire_adresse', 'destinataire_tel',
            'destinataire_email', 'destinataire_rccm', 'destinataire_ncc',
            'vehicule_marque', 'vehicule_modele', 'vehicule_immatriculation', 'vehicule_kilometrage',
            'date_livraison', 'lieu_livraison',
            'reference_client', 'objet',
            'transporteur', 'observations', 'status',
        ]
        widgets = {
            'date_livraison': forms.DateInput(attrs={'type': 'date'}),
            'observations': forms.Textarea(attrs={'rows': 2}),
        }
