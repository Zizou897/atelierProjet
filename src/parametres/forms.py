from django import forms
from django.core.files.uploadedfile import UploadedFile

from .models import CompanyProfile, DocumentDefaults

MAX_LOGO_SIZE = 2 * 1024 * 1024
ALLOWED_LOGO_FORMATS = {'JPEG', 'PNG', 'WEBP'}


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
        if isinstance(logo, UploadedFile) and logo.image.format not in ALLOWED_LOGO_FORMATS:
            raise forms.ValidationError('Le logo doit être une image JPG, PNG ou WEBP.')
        return logo

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.cleaned_data.get('remove_logo') and not isinstance(self.cleaned_data.get('logo'), UploadedFile):
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
