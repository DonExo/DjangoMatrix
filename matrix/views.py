from packaging.version import Version

from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Prefetch, Max
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PackageRequestForm
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


def packages_list(request):
    queryset = Package.objects.all()
    paginator = Paginator(queryset, settings.DEFAULT_NUMBER_OF_PACKAGES_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'matrix/package_list.html', context)


def package_details(request, slug):
    package = Package.objects.prefetch_related('versions').get(slug=slug)
    last_updated = None
    if package.repo_stats.exists():
        last_updated = package.repo_stats.latest('created_at').created_at
    versions_sorted = sorted(package.versions.all(), key=lambda v: Version(v.version), reverse=True)
    return render(request, 'matrix/package_details.html', {'package': package, 'versions_sorted': versions_sorted, 'last_updated': last_updated})


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


def package_add(request):
    if request.method == "POST":
        form = PackageRequestForm(request.POST)
        if form.is_valid():
            package_request = form.save(commit=False)
            package_request.save()
            messages.success(request, "Your package submission has been received. Thank you!")
            return redirect('packages')
        else:
            form = PackageRequestForm(request.POST)
    else:
        form = PackageRequestForm()

    return render(request, 'matrix/package_add.html', {'form': form})
