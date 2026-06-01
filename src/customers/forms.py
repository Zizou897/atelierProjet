from django import forms

from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "customer_type",
            "first_name",
            "last_name",
            "company_name",
            "email",
            "phone",
            "address_line1",
            "address_line2",
            "postal_code",
            "city",
            "country",
            "notes",
        ]
        labels = {
            "customer_type":  "Type de client",
            "first_name":     "Prénom",
            "last_name":      "Nom",
            "company_name":   "Raison sociale",
            "email":          "Adresse e-mail",
            "phone":          "Téléphone",
            "address_line1":  "Adresse (ligne 1)",
            "address_line2":  "Adresse (ligne 2)",
            "postal_code":    "Code postal",
            "city":           "Ville",
            "country":        "Pays",
            "notes":          "Notes internes",
        }
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        customer_type = cleaned_data.get("customer_type")
        first_name = (cleaned_data.get("first_name") or "").strip()
        last_name = (cleaned_data.get("last_name") or "").strip()
        company_name = (cleaned_data.get("company_name") or "").strip()

        if customer_type == Customer.CustomerType.INDIVIDUAL and not (first_name or last_name):
            raise forms.ValidationError(
                "Pour un particulier, renseignez au moins le prenom ou le nom."
            )

        if customer_type == Customer.CustomerType.COMPANY and not company_name:
            self.add_error("company_name", "Le nom de l'entreprise est obligatoire.")

        return cleaned_data
