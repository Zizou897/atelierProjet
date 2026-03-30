from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from datetime import timedelta

from .forms import CustomerForm
from .models import Customer
from vehicles.models import Vehicle


@login_required(login_url="login")
def customer_dashboard_view(request):
    today = timezone.localdate()
    selected_period = request.GET.get("period", "30")
    period_days_map = {"7": 7, "30": 30, "90": 90, "all": None}
    if selected_period not in period_days_map:
        selected_period = "30"

    all_customers = Customer.objects.all()
    if period_days_map[selected_period] is None:
        customers = all_customers
        period_label = "Toutes periodes"
    else:
        start_date = today - timedelta(days=period_days_map[selected_period])
        customers = all_customers.filter(created_at__date__gte=start_date)
        period_label = f"Derniers {selected_period} jours"

    total_customers = customers.count()
    active_customers = customers.filter(is_active=True).count()
    individual_customers = customers.filter(
        customer_type=Customer.CustomerType.INDIVIDUAL
    ).count()
    company_customers = customers.filter(
        customer_type=Customer.CustomerType.COMPANY
    ).count()

    linked_vehicle_count = Vehicle.objects.filter(customer__in=customers).count()
    customers_without_vehicle = customers.exclude(vehicles__isnull=False).distinct().count()
    inactive_customers = customers.filter(is_active=False).count()

    top_cities = (
        customers.exclude(city="")
        .values("city")
        .annotate(total=Count("id"))
        .order_by("-total", "city")[:5]
    )
    recent_customers = customers.order_by("-created_at")[:6]

    alerts = []
    if customers_without_vehicle > 0:
        alerts.append(
            {
                "level": "warning",
                "text": f"{customers_without_vehicle} client(s) sans vehicule rattache.",
            }
        )
    if inactive_customers > 0:
        alerts.append(
            {
                "level": "info",
                "text": f"{inactive_customers} client(s) inactif(s) sur la periode.",
            }
        )
    if not alerts:
        alerts.append({"level": "ok", "text": "Aucune alerte critique detectee."})

    context = {
        "today": today,
        "selected_period": selected_period,
        "period_label": period_label,
        "total_customers": total_customers,
        "active_customers": active_customers,
        "individual_customers": individual_customers,
        "company_customers": company_customers,
        "linked_vehicle_count": linked_vehicle_count,
        "customers_without_vehicle": customers_without_vehicle,
        "inactive_customers": inactive_customers,
        "top_cities": top_cities,
        "recent_customers": recent_customers,
        "alerts": alerts,
    }
    return render(request, "customers/dashboard.html", context)


@login_required(login_url="login")
def customer_list_view(request):
    query = request.GET.get("q", "").strip()
    customer_type = request.GET.get("type", "").strip()
    customers = Customer.objects.all()

    if query:
        customers = customers.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(company_name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone__icontains=query)
            | Q(city__icontains=query)
        )

    if customer_type:
        customers = customers.filter(customer_type=customer_type)

    context = {
        "customers": customers,
        "query": query,
        "selected_type": customer_type,
        "type_choices": Customer.CustomerType.choices,
    }
    return render(request, "customers/list.html", context)


@login_required(login_url="login")
@require_http_methods(["GET", "POST"])
def customer_create_view(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, "Client cree avec succes.")
            return redirect("customer_detail", customer_id=customer.id)
    else:
        form = CustomerForm()

    return render(
        request,
        "customers/form.html",
        {"form": form, "page_title": "Nouveau client", "is_create": True},
    )


@login_required(login_url="login")
@require_http_methods(["GET", "POST"])
def customer_update_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save()
            messages.success(request, "Client mis a jour.")
            return redirect("customer_detail", customer_id=customer.id)
    else:
        form = CustomerForm(instance=customer)

    return render(
        request,
        "customers/form.html",
        {
            "form": form,
            "customer": customer,
            "page_title": f"Modifier client: {customer.display_name}",
            "is_create": False,
        },
    )


@login_required(login_url="login")
def customer_detail_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    vehicles = Vehicle.objects.filter(customer=customer).order_by("registration_number")
    return render(
        request,
        "customers/detail.html",
        {
            "customer": customer,
            "vehicles": vehicles,
        },
    )
