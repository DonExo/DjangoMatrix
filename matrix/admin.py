from django.contrib import admin

from .models import DjangoVersion, PythonVersion, Compatibility


@admin.register(DjangoVersion)
class DjangoVersionAdmin(admin.ModelAdmin):
    list_display = ('id', 'version', 'release_date')


@admin.register(PythonVersion)
class PythonVersionAdmin(admin.ModelAdmin):
    list_display = ('id', 'version', 'release_date')


@admin.register(Compatibility)
class CompatibilityAdmin(admin.ModelAdmin):
    list_display = ('id', 'django_version', 'python_version', 'package', 'version')