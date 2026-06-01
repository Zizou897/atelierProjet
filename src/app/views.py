from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
import os


@login_required
def home(request):
    return render(request, 'app/layout/index.html', {})


@never_cache
def service_worker(request):
    sw_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'app', 'js', 'sw.js')
    with open(os.path.normpath(sw_path), 'r', encoding='utf-8') as f:
        content = f.read()
    return HttpResponse(content, content_type='application/javascript')


def offline(request):
    return render(request, 'offline.html', {})
