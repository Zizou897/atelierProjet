from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from customers.models import Customer
from .forms import InvoiceForm, ProformaForm
from .models import Invoice, InvoiceLine, InvoiceStatus, Proforma, ProformaLine, ProformaStatus


# ─────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────

@login_required
def invoice_dashboard(request):
    invoices_qs  = list(Invoice.objects.prefetch_related('lines').select_related('customer', 'proforma'))
    proformas_qs = list(Proforma.objects.prefetch_related('lines').select_related('customer'))

    # Financials (computed in Python — amounts are derived from line items)
    total_facture   = sum(inv.total_ttc for inv in invoices_qs)
    total_en_attente = sum(
        inv.net_a_payer for inv in invoices_qs
        if inv.status not in (InvoiceStatus.PAID, InvoiceStatus.CANCELLED)
    )

    # Counts by status
    inv_by_status = {}
    for inv in invoices_qs:
        inv_by_status[inv.status] = inv_by_status.get(inv.status, 0) + 1

    pf_by_status = {}
    for pf in proformas_qs:
        pf_by_status[pf.status] = pf_by_status.get(pf.status, 0) + 1

    # Pre-build status rows for template iteration
    inv_status_rows = [
        {'value': v, 'label': l, 'count': inv_by_status.get(v, 0)}
        for v, l in InvoiceStatus.choices
    ]
    pf_status_rows = [
        {'value': v, 'label': l, 'count': pf_by_status.get(v, 0)}
        for v, l in ProformaStatus.choices
    ]

    context = {
        'total_invoices':   len(invoices_qs),
        'total_proformas':  len(proformas_qs),
        'total_facture':    total_facture,
        'total_en_attente': total_en_attente,
        'inv_paid':     inv_by_status.get(InvoiceStatus.PAID, 0),
        'inv_overdue':  inv_by_status.get(InvoiceStatus.OVERDUE, 0),
        'pf_accepted':  pf_by_status.get(ProformaStatus.ACCEPTED, 0),
        'pf_converted': pf_by_status.get(ProformaStatus.CONVERTED, 0),
        'inv_status_rows': inv_status_rows,
        'pf_status_rows':  pf_status_rows,
        'recent_invoices':  sorted(invoices_qs,  key=lambda x: x.created_at, reverse=True)[:6],
        'recent_proformas': sorted(proformas_qs, key=lambda x: x.created_at, reverse=True)[:6],
    }
    return render(request, 'invoices/invoice_dashboard.html', context)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _parse_decimal(value, default=0):
    try:
        return Decimal(str(value).replace(' ', '').replace(',', '.') or default)
    except (InvalidOperation, ValueError):
        return Decimal(str(default))


def _save_proforma_lines(proforma, post):
    proforma.lines.all().delete()
    i = 0
    while f'line-{i}-designation' in post:
        designation = post.get(f'line-{i}-designation', '').strip()
        if designation:
            ProformaLine.objects.create(
                proforma=proforma,
                ordre=i + 1,
                designation=designation,
                quantite=_parse_decimal(post.get(f'line-{i}-quantite', '1'), 1),
                prix_unitaire=_parse_decimal(post.get(f'line-{i}-prix_unitaire', '0'), 0),
            )
        i += 1


def _save_invoice_lines(invoice, post):
    invoice.lines.all().delete()
    i = 0
    while f'line-{i}-designation' in post:
        designation = post.get(f'line-{i}-designation', '').strip()
        if designation:
            InvoiceLine.objects.create(
                invoice=invoice,
                ordre=i + 1,
                designation=designation,
                quantite=_parse_decimal(post.get(f'line-{i}-quantite', '1'), 1),
                unite=post.get(f'line-{i}-unite', '').strip(),
                prix_unitaire=_parse_decimal(post.get(f'line-{i}-prix_unitaire', '0'), 0),
                remise_pct=_parse_decimal(post.get(f'line-{i}-remise_pct', '0'), 0),
            )
        i += 1


# ─────────────────────────────────────────────
# Proforma views
# ─────────────────────────────────────────────

@login_required
def proforma_list(request):
    qs = Proforma.objects.prefetch_related('lines').select_related('customer')

    status_filter = request.GET.get('status', '')
    search = request.GET.get('q', '').strip()
    if status_filter:
        qs = qs.filter(status=status_filter)
    if search:
        qs = qs.filter(
            destinataire_nom__icontains=search,
        ) | qs.filter(numero__icontains=search) | qs.filter(objet__icontains=search)

    context = {
        'proformas': qs,
        'status_choices': ProformaStatus.choices,
        'status_filter': status_filter,
        'search': search,
    }
    return render(request, 'invoices/proforma_list.html', context)


@login_required
def proforma_create(request):
    customers = Customer.objects.filter(is_active=True).order_by('company_name', 'last_name')
    if request.method == 'POST':
        form = ProformaForm(request.POST)
        if form.is_valid():
            proforma = form.save(commit=False)
            proforma.created_by = request.user
            proforma.save()
            _save_proforma_lines(proforma, request.POST)
            messages.success(request, f"Proforma {proforma.numero} créé avec succès.")
            return redirect('proforma_detail', pk=proforma.pk)
    else:
        form = ProformaForm()
    return render(request, 'invoices/proforma_form.html', {
        'form': form, 'customers': customers, 'action': 'Nouveau proforma',
    })


@login_required
def proforma_detail(request, pk):
    proforma = get_object_or_404(Proforma.objects.prefetch_related('lines').select_related('customer'), pk=pk)
    return render(request, 'invoices/proforma_detail.html', {'proforma': proforma})


@login_required
def proforma_edit(request, pk):
    proforma = get_object_or_404(Proforma, pk=pk)
    customers = Customer.objects.filter(is_active=True).order_by('company_name', 'last_name')
    if request.method == 'POST':
        form = ProformaForm(request.POST, instance=proforma)
        if form.is_valid():
            form.save()
            _save_proforma_lines(proforma, request.POST)
            messages.success(request, f"Proforma {proforma.numero} mis à jour.")
            return redirect('proforma_detail', pk=proforma.pk)
    else:
        form = ProformaForm(instance=proforma)
    lines = list(proforma.lines.all())
    return render(request, 'invoices/proforma_form.html', {
        'form': form, 'proforma': proforma, 'customers': customers,
        'lines': lines, 'action': f'Modifier {proforma.numero}',
    })


@login_required
def proforma_delete(request, pk):
    proforma = get_object_or_404(Proforma, pk=pk)
    if request.method == 'POST':
        numero = proforma.numero
        proforma.delete()
        messages.success(request, f"Proforma {numero} supprimé.")
        return redirect('proforma_list')
    return render(request, 'invoices/confirm_delete.html', {
        'object': proforma, 'type': 'proforma',
        'cancel_url': 'proforma_detail',
    })


@login_required
def proforma_print(request, pk):
    proforma = get_object_or_404(Proforma.objects.prefetch_related('lines'), pk=pk)
    return render(request, 'invoices/proforma_print.html', {'proforma': proforma})


@login_required
def proforma_to_invoice(request, pk):
    proforma = get_object_or_404(Proforma.objects.prefetch_related('lines'), pk=pk)
    if proforma.status == ProformaStatus.CONVERTED:
        messages.warning(request, "Ce proforma a déjà été converti en facture.")
        return redirect('proforma_detail', pk=pk)
    if request.method == 'POST':
        invoice = Invoice.objects.create(
            proforma=proforma,
            customer=proforma.customer,
            destinataire_nom=proforma.destinataire_nom,
            destinataire_adresse=proforma.destinataire_adresse,
            destinataire_tel=proforma.destinataire_tel,
            destinataire_email=proforma.destinataire_email,
            destinataire_rccm_ncc=proforma.destinataire_rccm_ncc,
            date_emission=proforma.date_emission,
            reference_client=proforma.reference_client,
            objet=proforma.objet,
            bon_de_commande=proforma.bon_de_commande,
            remise_globale=proforma.remise_globale,
            tva_taux=proforma.tva_taux,
            created_by=request.user,
        )
        for line in proforma.lines.all():
            InvoiceLine.objects.create(
                invoice=invoice,
                ordre=line.ordre,
                designation=line.designation,
                quantite=line.quantite,
                prix_unitaire=line.prix_unitaire,
            )
        proforma.status = ProformaStatus.CONVERTED
        proforma.save()
        messages.success(request, f"Facture {invoice.numero} créée depuis le proforma {proforma.numero}.")
        return redirect('invoice_detail', pk=invoice.pk)
    return render(request, 'invoices/proforma_convert_confirm.html', {'proforma': proforma})


@login_required
def proforma_status(request, pk):
    proforma = get_object_or_404(Proforma, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(ProformaStatus.choices):
            proforma.status = new_status
            proforma.save()
            messages.success(request, f"Statut mis à jour : {proforma.get_status_display()}.")
    return redirect('proforma_detail', pk=pk)


# ─────────────────────────────────────────────
# Invoice views
# ─────────────────────────────────────────────

@login_required
def invoice_list(request):
    qs = Invoice.objects.prefetch_related('lines').select_related('customer', 'proforma')

    status_filter = request.GET.get('status', '')
    search = request.GET.get('q', '').strip()
    if status_filter:
        qs = qs.filter(status=status_filter)
    if search:
        qs = qs.filter(
            destinataire_nom__icontains=search,
        ) | qs.filter(numero__icontains=search) | qs.filter(objet__icontains=search)

    context = {
        'invoices': qs,
        'status_choices': InvoiceStatus.choices,
        'status_filter': status_filter,
        'search': search,
    }
    return render(request, 'invoices/invoice_list.html', context)


@login_required
def invoice_create(request):
    customers = Customer.objects.filter(is_active=True).order_by('company_name', 'last_name')
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.save()
            _save_invoice_lines(invoice, request.POST)
            messages.success(request, f"Facture {invoice.numero} créée avec succès.")
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm()
    return render(request, 'invoices/invoice_form.html', {
        'form': form, 'customers': customers, 'action': 'Nouvelle facture',
    })


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice.objects.prefetch_related('lines').select_related('customer', 'proforma'), pk=pk)
    return render(request, 'invoices/invoice_detail.html', {'invoice': invoice})


@login_required
def invoice_edit(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    customers = Customer.objects.filter(is_active=True).order_by('company_name', 'last_name')
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            _save_invoice_lines(invoice, request.POST)
            messages.success(request, f"Facture {invoice.numero} mise à jour.")
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm(instance=invoice)
    lines = list(invoice.lines.all())
    return render(request, 'invoices/invoice_form.html', {
        'form': form, 'invoice': invoice, 'customers': customers,
        'lines': lines, 'action': f'Modifier {invoice.numero}',
    })


@login_required
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        numero = invoice.numero
        invoice.delete()
        messages.success(request, f"Facture {numero} supprimée.")
        return redirect('invoice_list')
    return render(request, 'invoices/confirm_delete.html', {
        'object': invoice, 'type': 'invoice',
        'cancel_url': 'invoice_detail',
    })


@login_required
def invoice_print(request, pk):
    invoice = get_object_or_404(Invoice.objects.prefetch_related('lines'), pk=pk)
    return render(request, 'invoices/invoice_print.html', {'invoice': invoice})


@login_required
def invoice_status(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(InvoiceStatus.choices):
            invoice.status = new_status
            invoice.save()
            messages.success(request, f"Statut mis à jour : {invoice.get_status_display()}.")
    return redirect('invoice_detail', pk=pk)
