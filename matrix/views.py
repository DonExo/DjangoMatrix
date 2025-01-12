from collections import defaultdict

from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import render

from .models import DjangoVersion, PythonVersion, Package, Compatibility


def index(request):
    python_versions = PythonVersion.objects.prefetch_related(
        Prefetch(
            'compatibilities',
            queryset=Compatibility.objects.select_related('django_version').order_by('-django_version__release_date')
        )
    ).all()

    django_versions = DjangoVersion.objects.prefetch_related(
        Prefetch(
            'compatibilities',
            queryset=Compatibility.objects.select_related('python_version').order_by('-python_version__release_date')
        )
    ).all()

    context = {
        'python_versions': python_versions,
        'django_versions': django_versions,
    }
    return render(request, "matrix/index.html", context)
