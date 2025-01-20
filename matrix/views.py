from packaging.version import Version

from django.conf import settings
from django.contrib import messages
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import render, redirect

from django_tables2.views import SingleTableView

from .forms import PackageRequestForm
from .models import DjangoVersion, PythonVersion, Package, Compatibility
from .tables import PackageTable


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


class PackageListView(SingleTableView):
    model = Package
    table_class = PackageTable
    template_name = "matrix/package_list.html"
    paginate_by = settings.PACKAGES_PER_PAGE


def package_details(request, slug):
    package = Package.objects.prefetch_related('versions').get(slug=slug)
    versions_sorted = sorted(package.versions.all(), key=lambda v: Version(v.version), reverse=True)
    return render(request, 'matrix/package_details.html', {'package': package, 'versions_sorted': versions_sorted})


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
            form.save_m2m()
            messages.success(request, "Your package submission has been received. Thank you!")
            return redirect('packages')
        else:
            form = PackageRequestForm(request.POST)
    else:
        form = PackageRequestForm()

    return render(request, 'matrix/package_add.html', {'form': form})


def custom_404(request, exception):
    return render(request, '404.html', status=404)


def custom_500(request, exception):
    return render(request, '404.html', {"foo": "bar"}, status=500)
