import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import PortalUserCreateForm, PortalUserUpdateForm, RoleForm
from .models import Role, UserProfile

logger = logging.getLogger(__name__)
User = get_user_model()


@require_http_methods(["GET", "POST"])
def login_view(request):
    """Vue de connexion pour tous les utilisateurs CTAMS."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        remember_me = request.POST.get("remember_me", False)

        if not username or not password:
            return render(
                request,
                "login/index.html",
                {"error": "Veuillez entrer vos identifiants."},
                status=400,
            )

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                logger.warning("Tentative connexion compte inactif: %s", username)
                return render(
                    request,
                    "login/index.html",
                    {"error": "Votre compte est desactive. Contactez l'administrateur."},
                    status=403,
                )

            if user.is_superuser or user.is_staff:
                logger.warning("Tentative connexion compte admin Django via portail: %s", username)
                return render(
                    request,
                    "login/index.html",
                    {
                        "error": (
                            "Les comptes administration Django ne sont pas autorises "
                            "sur ce portail."
                        )
                    },
                    status=403,
                )

            profile, _ = UserProfile.objects.get_or_create(user=user)
            if not profile.portal_active:
                logger.warning("Tentative connexion compte portail desactive: %s", username)
                return render(
                    request,
                    "login/index.html",
                    {"error": "Votre acces portail est desactive. Contactez l'administrateur."},
                    status=403,
                )

            login(request, user)
            logger.info("Connexion reussie: %s", username)

            if remember_me:
                request.session.set_expiry(30 * 24 * 60 * 60)  # 30 jours
            else:
                request.session.set_expiry(0)  # Session navigateur

            next_page = request.GET.get("next", "dashboard")
            return redirect(next_page)

        logger.warning("Tentative connexion echouee: %s", username)
        return render(
            request,
            "login/index.html",
            {"error": "Identifiant ou mot de passe incorrect."},
            status=401,
        )

    return render(request, "login/index.html")


@login_required(login_url="login")
@require_http_methods(["GET"])
def logout_view(request):
    """Deconnexion utilisateur."""
    username = request.user.username
    logout(request)
    logger.info("Deconnexion: %s", username)
    messages.success(request, "Vous avez ete deconnecte avec succes.")
    return redirect("login")


@login_required(login_url="login")
def dashboard(request):
    """Dashboard principal commun a tous les roles."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    user_role = profile.role.code if profile.role else "STANDARD"
    modules = [
        {
            "name": "Clients",
            "description": "Base clients, suivi des contacts et historique des interventions.",
            "icon": "fa-users",
            "url": "/customers/dashboard/",
        },
        {
            "name": "Vehicules",
            "description": "Parc vehicules, fiches techniques et suivi des passages atelier.",
            "icon": "fa-car-side",
            "url": "/vehicles/dashboard/",
        },
        {
            "name": "Atelier",
            "description": "Planification, interventions en cours et assignation techniciens.",
            "icon": "fa-screwdriver-wrench",
            "url": "/workshop/dashboard/",
        },
        {
            "name": "Devis",
            "description": "Creation, validation et conversion des devis en ordres de travail.",
            "icon": "fa-file-signature",
            "url": "#",
        },
        {
            "name": "Factures",
            "description": "Facturation, suivi des reglements et relances clients.",
            "icon": "fa-file-invoice-dollar",
            "url": "#",
        },
        {
            "name": "Reporting",
            "description": "KPI activite, performance atelier et suivi des objectifs.",
            "icon": "fa-chart-line",
            "url": "#",
        },
        {
            "name": "Audit & Logs",
            "description": "Tracabilite des actions et securite des operations metier.",
            "icon": "fa-shield-halved",
            "url": "#",
        },
    ]

    if request.user.has_perm("users.manage_users"):
        modules.append(
            {
                "name": "Utilisateurs",
                "description": "Gestion des users, roles et permissions applicatives.",
                "icon": "fa-users-gear",
                "url": "/auth/users/",
            }
        )

    context = {
        "user": request.user,
        "role": user_role,
        "modules": modules,
    }
    return render(request, "dashboard.html", context)


def forgot_password_view(request):
    """Page oubli mot de passe."""
    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        if not email:
            return render(
                request,
                "login/forgot_password.html",
                {"error": "Veuillez entrer votre email."},
                status=400,
            )

        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            User.objects.get(email=email)
            logger.info("Demande reinitialisation password: %s", email)
            return render(
                request,
                "login/forgot_password.html",
                {
                    "success": (
                        "Un email de reinitialisation a ete envoye. "
                        "Consultez votre boite mail."
                    )
                },
            )
        except User.DoesNotExist:
            logger.warning("Tentative reinitialisation email inexistant: %s", email)
            return render(
                request,
                "login/forgot_password.html",
                {
                    "success": (
                        "Un email de reinitialisation a ete envoye. "
                        "Consultez votre boite mail."
                    )
                },
            )

    return render(request, "login/forgot_password.html")


def contact_admin_view(request):
    """Page contact administrateur pour creer un compte."""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        if not all([name, email, message]):
            return render(
                request,
                "login/contact-admin.html",
                {"error": "Tous les champs sont obligatoires."},
                status=400,
            )

        logger.info("Nouvelle demande de compte: %s (%s)", name, email)
        # TODO: Envoyer email a l'admin

        return render(
            request,
            "login/contact-admin.html",
            {
                "success": (
                    "Votre demande a ete envoyee. "
                    "L'administrateur vous contactera bientot."
                )
            },
        )

    return render(request, "login/contact-admin.html")


@login_required(login_url="login")
@permission_required("users.manage_users", raise_exception=True)
def user_list_view(request):
    query = request.GET.get("q", "").strip()
    role_code = request.GET.get("role", "").strip()

    users = User.objects.select_related("profile", "profile__role").order_by("username")

    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )

    if role_code:
        users = users.filter(profile__role__code=role_code)

    context = {
        "users": users,
        "roles": Role.objects.filter(is_active=True),
        "query": query,
        "selected_role": role_code,
    }
    return render(request, "users/list.html", context)


@login_required(login_url="login")
@permission_required("users.manage_users", raise_exception=True)
@require_http_methods(["GET", "POST"])
def user_create_view(request):
    if request.method == "POST":
        form = PortalUserCreateForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                password=form.cleaned_data["password1"],
                is_active=form.cleaned_data["is_active"],
            )

            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = form.cleaned_data["role"]
            profile.phone = form.cleaned_data["phone"]
            profile.portal_active = form.cleaned_data["portal_active"]
            profile.save()

            user.groups.set(form.cleaned_data["groups"])
            user.user_permissions.set(form.cleaned_data["user_permissions"])

            messages.success(request, "Utilisateur cree avec succes.")
            return redirect("user_update", user_id=user.id)
    else:
        form = PortalUserCreateForm()

    return render(
        request,
        "users/form.html",
        {"form": form, "page_title": "Nouvel utilisateur", "is_create": True},
    )


@login_required(login_url="login")
@permission_required("users.manage_users", raise_exception=True)
@require_http_methods(["GET", "POST"])
def user_update_view(request, user_id):
    managed_user = get_object_or_404(User.objects.select_related("profile"), id=user_id)

    if request.method == "POST":
        form = PortalUserUpdateForm(request.POST, user_instance=managed_user)
        if form.is_valid():
            managed_user.email = form.cleaned_data["email"]
            managed_user.first_name = form.cleaned_data["first_name"]
            managed_user.last_name = form.cleaned_data["last_name"]
            managed_user.is_active = form.cleaned_data["is_active"]
            managed_user.save()

            profile, _ = UserProfile.objects.get_or_create(user=managed_user)
            profile.role = form.cleaned_data["role"]
            profile.phone = form.cleaned_data["phone"]
            profile.portal_active = form.cleaned_data["portal_active"]
            profile.save()

            managed_user.groups.set(form.cleaned_data["groups"])
            managed_user.user_permissions.set(form.cleaned_data["user_permissions"])

            new_password = form.cleaned_data["new_password"]
            if new_password:
                managed_user.set_password(new_password)
                managed_user.save()

            messages.success(request, "Utilisateur mis a jour.")
            return redirect("user_update", user_id=managed_user.id)
    else:
        form = PortalUserUpdateForm(user_instance=managed_user)

    return render(
        request,
        "users/form.html",
        {
            "form": form,
            "managed_user": managed_user,
            "page_title": f"Modifier utilisateur: {managed_user.username}",
            "is_create": False,
        },
    )


@login_required(login_url="login")
@permission_required("users.manage_users", raise_exception=True)
@require_http_methods(["GET", "POST"])
def role_list_view(request):
    if request.method == "POST":
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Role enregistre.")
            return redirect("role_list")
    else:
        form = RoleForm()

    context = {
        "form": form,
        "roles": Role.objects.all(),
    }
    return render(request, "users/roles.html", context)
