from django.contrib import admin

from .models import DjangoVersion, PythonVersion, Compatibility, Package, PackageVersion, PackageRepoStats


class CompatibilityInline(admin.TabularInline):
    model = Compatibility
    extra = 1
    autocomplete_fields = ['django_version']

class PackageVersionInline(admin.TabularInline):
    model = PackageVersion
    extra = 1

@admin.register(DjangoVersion)
class DjangoVersionAdmin(admin.ModelAdmin):
    list_display = ('version', 'release_date')
    search_fields = ['version']

@admin.register(PythonVersion)
class PythonVersionAdmin(admin.ModelAdmin):
    list_display = ('version', 'release_date')
    inlines = [CompatibilityInline]


@admin.register(Compatibility)
class CompatibilityAdmin(admin.ModelAdmin):
    list_display = ('id', 'django_version', 'python_version', 'package', 'version')


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('id', 'name', 'slug', 'metric_stars', 'metric_forks')
    inlines = [PackageVersionInline]


@admin.register(PackageRepoStats)
class PackageRepoStatsAdmin(admin.ModelAdmin):
    list_display = ('package', 'created_at', 'metric_stars', 'metric_forks', 'metric_open_issues')
    list_filter = ('created_at', 'package')
    readonly_fields = ('created_at', )
