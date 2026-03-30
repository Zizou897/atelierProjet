from django import forms

from .models import Vehicle


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            "customer",
            "registration_number",
            "vin",
            "make",
            "model",
            "trim",
            "first_registration_date",
            "fuel_type",
            "transmission",
            "mileage",
            "color",
            "owner_name",
            "owner_phone",
            "owner_email",
            "notes",
        ]
        widgets = {
            "first_registration_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        customer = cleaned_data.get("customer")
        owner_name = (cleaned_data.get("owner_name") or "").strip()

        if customer and not owner_name:
            cleaned_data["owner_name"] = customer.display_name

        return cleaned_data

    def clean_registration_number(self):
        value = self.cleaned_data["registration_number"].strip().upper().replace(" ", "-")
        return value

    def clean_vin(self):
        value = self.cleaned_data.get("vin")
        if not value:
            return value
        return value.strip().upper()
