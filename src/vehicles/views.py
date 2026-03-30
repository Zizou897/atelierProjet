from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from workshop.forms import WorkshopVisitForm
from workshop.models import Maintenance, Technician, WorkshopVisit

from .forms import VehicleForm
from .models import Vehicle


def _technician_options():
    return Technician.objects.order_by("last_name", "first_name")


@login_required(login_url="login")
def vehicle_dashboard_view(request):
    today = timezone.localdate()
    selected_period = request.GET.get("period", "30")
    period_days_map = {"7": 7, "30": 30, "90": 90, "all": None}
    if selected_period not in period_days_map:
        selected_period = "30"

    all_vehicles = Vehicle.objects.select_related("customer")
    if period_days_map[selected_period] is None:
        vehicles = all_vehicles
        period_label = "Toutes periodes"
    else:
        start_date = today - timedelta(days=period_days_map[selected_period])
        vehicles = all_vehicles.filter(created_at__date__gte=start_date)
        period_label = f"Derniers {selected_period} jours"

    total_vehicles = vehicles.count()
    linked_customer_count = vehicles.filter(customer__isnull=False).count()
    unlinked_count = total_vehicles - linked_customer_count

    by_fuel = (
        vehicles.values("fuel_type")
        .annotate(total=Count("id"))
        .order_by("-total", "fuel_type")
    )
    recent_vehicles = vehicles.order_by("-created_at")[:6]
    high_mileage_count = vehicles.filter(mileage__gte=200000).count()
    without_visit_count = vehicles.filter(workshop_visits__isnull=True).distinct().count()

    alerts = []
    if unlinked_count > 0:
        alerts.append(
            {
                "level": "warning",
                "text": f"{unlinked_count} vehicule(s) sans client rattache.",
            }
        )
    if high_mileage_count > 0:
        alerts.append(
            {
                "level": "warning",
                "text": f"{high_mileage_count} vehicule(s) ont un kilometrage eleve (>= 200000 km).",
            }
        )
    if without_visit_count > 0:
        alerts.append(
            {
                "level": "info",
                "text": f"{without_visit_count} vehicule(s) sans historique atelier.",
            }
        )
    if not alerts:
        alerts.append({"level": "ok", "text": "Aucune alerte critique detectee."})

    context = {
        "today": today,
        "selected_period": selected_period,
        "period_label": period_label,
        "total_vehicles": total_vehicles,
        "linked_customer_count": linked_customer_count,
        "unlinked_count": unlinked_count,
        "high_mileage_count": high_mileage_count,
        "without_visit_count": without_visit_count,
        "by_fuel": by_fuel,
        "recent_vehicles": recent_vehicles,
        "alerts": alerts,
    }
    return render(request, "vehicles/dashboard.html", context)


@login_required(login_url="login")
def vehicle_list_view(request):
    query = request.GET.get("q", "").strip()
    vehicles = Vehicle.objects.select_related("customer")

    if query:
        vehicles = vehicles.filter(
            Q(registration_number__icontains=query)
            | Q(vin__icontains=query)
            | Q(make__icontains=query)
            | Q(model__icontains=query)
            | Q(owner_name__icontains=query)
            | Q(customer__first_name__icontains=query)
            | Q(customer__last_name__icontains=query)
            | Q(customer__company_name__icontains=query)
        )

    context = {
        "vehicles": vehicles,
        "query": query,
    }
    return render(request, "vehicles/list.html", context)


@login_required(login_url="login")
def vehicle_create_view(request):
    if request.method == "POST":
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save()
            messages.success(request, "Vehicule cree avec succes.")
            return redirect("vehicle_detail", vehicle_id=vehicle.id)
    else:
        form = VehicleForm()

    return render(
        request,
        "vehicles/form.html",
        {"form": form, "page_title": "Nouveau vehicule"},
    )


@login_required(login_url="login")
def vehicle_update_view(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    if request.method == "POST":
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            vehicle = form.save()
            messages.success(request, "Fiche vehicule mise a jour.")
            return redirect("vehicle_detail", vehicle_id=vehicle.id)
    else:
        form = VehicleForm(instance=vehicle)

    return render(
        request,
        "vehicles/form.html",
        {"form": form, "vehicle": vehicle, "page_title": "Modifier la fiche vehicule"},
    )


@login_required(login_url="login")
def vehicle_detail_view(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle.objects.select_related("customer"), id=vehicle_id)
    visits = WorkshopVisit.objects.filter(vehicle=vehicle)

    context = {
        "vehicle": vehicle,
        "visits": visits,
    }
    return render(request, "vehicles/detail.html", context)


@login_required(login_url="login")
def vehicle_visit_create_view(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    blocking_statuses = [
        WorkshopVisit.VisitStatus.OPEN,
        WorkshopVisit.VisitStatus.IN_PROGRESS,
    ]
    technicians = _technician_options()

    if request.method == "POST":
        form = WorkshopVisitForm(request.POST)
        if form.is_valid():
            today = timezone.localdate()
            has_active_visit = WorkshopVisit.objects.filter(
                vehicle=vehicle,
                status__in=blocking_statuses,
            ).exists()
            if has_active_visit:
                form.add_error(
                    None,
                    "Impossible de creer un nouveau passage: le precedent n'est pas termine.",
                )
                return render(
                    request,
                    "workshop/visit_form.html",
                    {
                        "form": form,
                        "vehicle": vehicle,
                        "page_title": "Nouveau passage atelier",
                        "technicians": technicians,
                    },
                )

            visit = form.save(commit=False)
            visit.vehicle = vehicle
            visit.visit_date = today
            visit.start_date = today
            if visit.status == WorkshopVisit.VisitStatus.DONE:
                maintenance_status = Maintenance.MaintenanceStatus.DONE
                visit.end_date = today
            elif visit.status == WorkshopVisit.VisitStatus.CANCELED:
                maintenance_status = Maintenance.MaintenanceStatus.CANCELED
                visit.end_date = None
            else:
                maintenance_status = Maintenance.MaintenanceStatus.OPEN
                visit.end_date = None
            maintenance = Maintenance.objects.create(
                vehicle=vehicle,
                opened_on=visit.start_date,
                status=maintenance_status,
                notes=f"{visit.get_service_display()} - {visit.concern}",
            )
            visit.maintenance = maintenance
            visit.save()

            if visit.mileage_at_visit > vehicle.mileage:
                vehicle.mileage = visit.mileage_at_visit
                vehicle.save(update_fields=["mileage", "updated_at"])

            messages.success(request, "Passage atelier enregistre.")
            return redirect("vehicle_detail", vehicle_id=vehicle.id)
    else:
        form = WorkshopVisitForm(
            initial={
                "mileage_at_visit": vehicle.mileage,
            }
        )

    return render(
        request,
        "workshop/visit_form.html",
        {
            "form": form,
            "vehicle": vehicle,
            "page_title": "Nouveau passage atelier",
            "technicians": technicians,
        },
    )


@login_required(login_url="login")
def vehicle_visit_update_view(request, vehicle_id, visit_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    visit = get_object_or_404(WorkshopVisit, id=visit_id, vehicle=vehicle)
    technicians = _technician_options()

    if request.method == "POST":
        form = WorkshopVisitForm(request.POST, instance=visit)
        if form.is_valid():
            today = timezone.localdate()
            visit = form.save()

            if not visit.start_date:
                visit.start_date = today

            if visit.status == WorkshopVisit.VisitStatus.DONE:
                maintenance_status = Maintenance.MaintenanceStatus.DONE
                visit.end_date = today
            elif visit.status == WorkshopVisit.VisitStatus.CANCELED:
                maintenance_status = Maintenance.MaintenanceStatus.CANCELED
                visit.end_date = None
            else:
                maintenance_status = Maintenance.MaintenanceStatus.OPEN
                visit.end_date = None

            visit.save(update_fields=["start_date", "end_date", "updated_at"])

            if visit.maintenance:
                visit.maintenance.opened_on = visit.start_date
                visit.maintenance.status = maintenance_status
                visit.maintenance.notes = f"{visit.get_service_display()} - {visit.concern}"
                visit.maintenance.save(
                    update_fields=["opened_on", "status", "notes", "updated_at"]
                )

            if visit.mileage_at_visit > vehicle.mileage:
                vehicle.mileage = visit.mileage_at_visit
                vehicle.save(update_fields=["mileage", "updated_at"])

            messages.success(request, "Passage atelier mis a jour.")
            return redirect("vehicle_detail", vehicle_id=vehicle.id)
    else:
        form = WorkshopVisitForm(instance=visit)

    return render(
        request,
        "workshop/visit_form.html",
        {
            "form": form,
            "vehicle": vehicle,
            "page_title": "Modifier passage atelier",
            "technicians": technicians,
        },
    )
