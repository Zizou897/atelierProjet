from django.contrib import admin
from .models import Invoice, InvoiceLine, Proforma, ProformaLine


class ProformaLineInline(admin.TabularInline):
    model = ProformaLine
    extra = 1
    fields = ['ordre', 'designation', 'quantite', 'prix_unitaire']


class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 1
    fields = ['ordre', 'designation', 'quantite', 'unite', 'prix_unitaire', 'remise_pct']


@admin.register(Proforma)
class ProformaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'destinataire_nom', 'date_emission', 'status', 'total_ttc']
    list_filter = ['status', 'date_emission']
    search_fields = ['numero', 'destinataire_nom', 'objet']
    inlines = [ProformaLineInline]
    readonly_fields = ['numero', 'created_at', 'updated_at']

    def total_ttc(self, obj):
        return f"{obj.total_ttc:,} FCFA"
    total_ttc.short_description = 'Total TTC'


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['numero', 'destinataire_nom', 'date_emission', 'date_echeance', 'status', 'total_ttc']
    list_filter = ['status', 'date_emission']
    search_fields = ['numero', 'destinataire_nom', 'objet']
    inlines = [InvoiceLineInline]
    readonly_fields = ['numero', 'created_at', 'updated_at']

    def total_ttc(self, obj):
        return f"{obj.total_ttc:,} FCFA"
    total_ttc.short_description = 'Total TTC'
