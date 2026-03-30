from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import TechnicianForm
from .models import Technician, WorkshopVisit


@login_required(login_url="login")
def workshop_dashboard_view(request):
    technician_form = TechnicianForm()
    if request.method == "POST":
        technician_form = TechnicianForm(request.POST)
        if technician_form.is_valid():
            technician = technician_form.save()
            messages.success(
                request,
                f"Technicien {technician.full_name} enregistré avec succès.",
            )
            return redirect("workshop_dashboard")

    today = timezone.localdate()
    selected_period = request.GET.get("period", "30")
    period_days_map = {"7": 7, "30": 30, "90": 90, "all": None}
    if selected_period not in period_days_map:
        selected_period = "30"

    all_visits = WorkshopVisit.objects.select_related("vehicle")
    if period_days_map[selected_period] is None:
        visits = all_visits
        period_label = "Toutes periodes"
    else:
        start_date = today - timedelta(days=period_days_map[selected_period])
        visits = all_visits.filter(visit_date__gte=start_date)
        period_label = f"Derniers {selected_period} jours"

    total_visits = visits.count()
    open_visits = visits.filter(status=WorkshopVisit.VisitStatus.OPEN).count()
    in_progress_visits = visits.filter(status=WorkshopVisit.VisitStatus.IN_PROGRESS).count()
    done_visits = visits.filter(status=WorkshopVisit.VisitStatus.DONE).count()
    overdue_open_count = visits.filter(
        status__in=[WorkshopVisit.VisitStatus.OPEN, WorkshopVisit.VisitStatus.IN_PROGRESS],
        visit_date__lte=today - timedelta(days=7),
    ).count()

    top_technicians = (
        visits.exclude(technician_name="")
        .values("technician_name")
        .annotate(total=Count("id"))
        .order_by("-total", "technician_name")[:5]
    )
    recent_visits = visits.order_by("-visit_date", "-id")[:8]

    alerts = []
    if overdue_open_count > 0:
        alerts.append(
            {
                "level": "warning",
                "text": f"{overdue_open_count} passage(s) ouverts/en cours depuis plus de 7 jours.",
            }
        )
    if open_visits > 0:
        alerts.append(
            {
                "level": "info",
                "text": f"{open_visits} passage(s) encore a planifier (statut Ouvert).",
            }
        )
    if not alerts:
        alerts.append({"level": "ok", "text": "Aucune alerte critique detectee."})

    technician_count = Technician.objects.count()

    context = {
        "today": today,
        "selected_period": selected_period,
        "period_label": period_label,
        "total_visits": total_visits,
        "open_visits": open_visits,
        "in_progress_visits": in_progress_visits,
        "done_visits": done_visits,
        "overdue_open_count": overdue_open_count,
        "top_technicians": top_technicians,
        "recent_visits": recent_visits,
        "alerts": alerts,
        "technician_count": technician_count,
        "technician_form": technician_form,
    }
    return render(request, "workshop/dashboard.html", context)


@login_required(login_url="login")
def workshop_visit_list_view(request):
    query = request.GET.get("q", "").strip()
    visits = WorkshopVisit.objects.select_related("vehicle")

    if query:
        visits = visits.filter(
            Q(vehicle__registration_number__icontains=query)
            | Q(vehicle__make__icontains=query)
            | Q(vehicle__model__icontains=query)
            | Q(service__icontains=query)
            | Q(concern__icontains=query)
            | Q(technician_name__icontains=query)
        )

    context = {
        "visits": visits,
        "query": query,
    }
    return render(request, "workshop/visit_list.html", context)


@login_required(login_url="login")
def technician_list_view(request):
    query = request.GET.get("q", "").strip()
    technicians = Technician.objects.all()

    if query:
        technicians = technicians.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(position__icontains=query)
            | Q(contact__icontains=query)
            | Q(identification_number__icontains=query)
            | Q(atelier__icontains=query)
        )

    context = {
        "technicians": technicians,
        "query": query,
    }
    return render(request, "workshop/technician_list.html", context)


@login_required(login_url="login")
def technician_create_view(request):
    if request.method == "POST":
        form = TechnicianForm(request.POST)
        if form.is_valid():
            technician = form.save()
            messages.success(
                request, f"Technicien {technician.full_name} enregistré avec succès."
            )
            return redirect("workshop_technician_list")
    else:
        form = TechnicianForm()

    return render(
        request,
        "workshop/technician_form.html",
        {"form": form, "page_title": "Nouvel technicien"},
    )
