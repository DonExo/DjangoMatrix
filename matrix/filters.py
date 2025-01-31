import django_filters
from .models import Package


class PackageFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Search Packages'
    )

    class Meta:
        model = Package
        fields = []