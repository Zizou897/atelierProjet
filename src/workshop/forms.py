from django import forms

from .models import Technician, WorkshopVisit


class WorkshopVisitForm(forms.ModelForm):
    class Meta:
        model = WorkshopVisit
        fields = [
            "mileage_at_visit",
            "service",
            "concern",
            "diagnosis",
            "work_performed",
            "technician_name",
            "status",
            "estimated_cost",
            "actual_cost",
            "next_visit_date",
        ]
        widgets = {
            "next_visit_date": forms.DateInput(attrs={"type": "date"}),
            "diagnosis": forms.Textarea(attrs={"rows": 3}),
            "work_performed": forms.Textarea(attrs={"rows": 3}),
            "technician_name": forms.TextInput(attrs={"list": "technicians-list", "autocomplete": "off"}),
        }


class TechnicianForm(forms.ModelForm):
    class Meta:
        model = Technician
        fields = [
            "first_name",
            "last_name",
            "position",
            "contact",
            "identification_number",
            "atelier",
        ]
        widgets = {
            "atelier": forms.Select(),
        }
