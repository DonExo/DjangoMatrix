from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

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

    packages = Package.objects.all()[:10]

    context = {
        'python_versions': python_versions,
        'django_versions': django_versions,
        'most_popular_packages': packages,
    }
    return render(request, "matrix/index.html", context)


def packages(request):
    queryset = Package.objects.all()
    paginator = Paginator(queryset, settings.DEFAULT_NUMBER_OF_PACKAGES_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'matrix/packages.html', context)


def package_details(request, slug):
    package = get_object_or_404(Package, slug=slug)
    return render(request, 'matrix/package_details.html', {'package': package})


def package_search(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        packages = Package.objects.filter(name__icontains=query)
        for package in packages:
            results.append({
                'id': package.id,
                'name': package.name,
                'slug': package.slug,
            })
    return JsonResponse({'results': results})