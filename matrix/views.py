from packaging.version import Version

from django.conf import settings
from django.contrib import messages
from django.db.models import Prefetch, Count
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_page

from django_filters.views import BaseFilterView
from django_tables2 import RequestConfig
from django_tables2.views import SingleTableView

from .filters import PackageFilter
from .forms import PackageRequestForm, ContactForm
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

    packages = Package.objects.all()
    most_popular_packages = packages[:10]

    context = {
        'python_versions': python_versions,
        'django_versions': django_versions,
        'most_popular_packages': most_popular_packages,
        'packages_count': packages.count(),
    }
    return render(request, "matrix/index.html", context)


@cache_page(60 * 60 * 24, key_prefix="package_details")  # Cache for 24 hours
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


class PackageListView(BaseFilterView, SingleTableView):
    model = Package
    table_class = PackageTable
    template_name = "matrix/package_list.html"
    paginate_by = settings.PACKAGES_PER_PAGE_DEFAULT
    filterset_class = PackageFilter

    def get_queryset(self):
        qs = super().get_queryset()
        self.filterset = self.filterset_class(self.request.GET, queryset=qs)  # apply filters
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        RequestConfig(self.request,paginate={'per_page': self.get_paginate_by()}).configure(context['table'])
        context['filter'] = self.filterset
        context['per_page_options'] = settings.PACKAGES_PER_PAGE_OPTIONS
        return context

    def get_paginate_by(self, queryset=None):
        per_page = self.request.GET.get('per_page', settings.PACKAGES_PER_PAGE_DEFAULT)
        try:
            return int(per_page)
        except (ValueError, TypeError):
            return settings.PACKAGES_PER_PAGE_DEFAULT


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save(commit=False)
            # Extract client IP from X-Forwarded-For header
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
            if x_forwarded_for:
                client_ip = x_forwarded_for.split(',')[0].strip()
            else:
                client_ip = request.META.get('REMOTE_ADDR', '')
            contact_message.ip_address = client_ip
            contact_message.save()
            messages.info(request, "Your message has been sent. Thank you!")
            return redirect('index')
        else:
            messages.error(request, "There has been an error. Please try again.")
    else:
        form = ContactForm()

    return render(request, '__pages/contact.html', {'form': form})


def custom_404(request, exception):
    return render(request, '__pages/404.html', status=404)


def custom_500(request, exception):
    return render(request, '__pages/404.html', status=500)
