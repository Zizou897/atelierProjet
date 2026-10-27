from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import CompanyProfileForm, DocumentDefaultsForm
from .models import CompanyProfile, DocumentDefaults

TABS = (
    ('ctams', 'CTAMS'),
    ('cta', 'CTA'),
    ('documents', 'Documents'),
)
TAB_KEYS = [key for key, _ in TABS]


@login_required(login_url='login')
@permission_required('users.manage_users', raise_exception=True)
@require_http_methods(['GET', 'POST'])
def settings_home(request):
    tab = request.GET.get('onglet', 'ctams')
    if tab not in TAB_KEYS:
        tab = 'ctams'

    if tab == 'documents':
        form_class, instance, profile = DocumentDefaultsForm, DocumentDefaults.load(), None
    else:
        profile = get_object_or_404(CompanyProfile, key=tab)
        form_class, instance = CompanyProfileForm, profile

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paramètres enregistrés.')
            return redirect(f"{reverse('settings_home')}?onglet={tab}")
    else:
        form = form_class(instance=instance)

    return render(request, 'parametres/settings.html', {
        'tabs': TABS,
        'tab': tab,
        'form': form,
        'profile': profile,
    })
