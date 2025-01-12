from django.contrib import admin

from .models import DjangoVersion, PythonVersion, Compatibility, Package, PackageVersion


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
    list_display = ('name', 'slug', 'popularity_metric')
    inlines = [PackageVersionInline]
