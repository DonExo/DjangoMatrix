from packaging.version import Version

from django.conf import settings
from django.contrib import messages
from django.db.models import Prefetch, Count
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_page

from django_tables2.views import SingleTableView

from .forms import PackageRequestForm
from .graphs import get_package_graph
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


@cache_page(60 * 60 * 24, key_prefix="package_details")
def package_details(request, slug):
    package = get_object_or_404(Package.objects.prefetch_related('versions'), slug=slug)
    versions_sorted = sorted(package.versions.prefetch_related("django_compatibility").all(),
                             key=lambda v: Version(v.version), reverse=True)
    graph_html = get_package_graph(package)
    excluded_topics = ["python", "django"]
    topics_to_match = package.topics.exclude(name__in=excluded_topics)
    similar_packages = (
        Package.objects
        .filter(topics__name__in=topics_to_match.values_list('name', flat=True))
        .exclude(pk=package.pk)
        .annotate(shared_topic_count=Count('topics__name'))
        .order_by('-shared_topic_count')
        .distinct()
    )

    context = {
        "package": package,
        "versions_sorted": versions_sorted,
        "graph_html": graph_html,
        "similar_packages": similar_packages
    }
    return render(request, 'matrix/package_details.html', context)


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


class PackageListView(SingleTableView):
    model = Package
    table_class = PackageTable
    template_name = "matrix/package_list.html"
    paginate_by = settings.PACKAGES_PER_PAGE_DEFAULT

    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get('per_page', settings.PACKAGES_PER_PAGE_DEFAULT)
        try:
            per_page = int(per_page)
            if per_page in settings.PACKAGES_PER_PAGE_OPTIONS:
                return per_page
            return self.paginate_by
        except (ValueError, TypeError):
            return self.paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['per_page_options'] = settings.PACKAGES_PER_PAGE_OPTIONS
        return context


def custom_404(request, exception):
    return render(request, '404.html', status=404)


def custom_500(request, exception):
    return render(request, '404.html', {"foo": "bar"}, status=500)
