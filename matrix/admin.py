from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .models import DjangoVersion, PythonVersion, Compatibility, Package, PackageVersion, PackageRepoStats, \
    PackageRequest, PackageTopic, ContactMessage, Category


class CompatibilityInline(admin.TabularInline):
    model = Compatibility
    extra = 1
    autocomplete_fields = ['django_version']


class PackageVersionInline(admin.TabularInline):
    model = PackageVersion
    extra = 0

class CategoryInline(admin.TabularInline):
    model = Package.categories.through
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
    list_filter = ('django_version', 'python_version')


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'slug', 'metric_stars', 'metric_forks', 'display_categories')
    search_fields = ['name__icontains', 'slug__icontains', 'description__icontains']
    inlines = [PackageVersionInline]

    def display_categories(self, obj):
        return ", ".join(cat.name for cat in obj.categories.all())
    display_categories.short_description = 'Categories'


@admin.register(PackageVersion)
class PackageVersionAdmin(admin.ModelAdmin):
    list_display = ('package', 'version', 'release_date')
    search_fields = ('package__name', )


@admin.register(PackageRepoStats)
class PackageRepoStatsAdmin(admin.ModelAdmin):
    list_display = ('package', 'created_at', 'metric_stars', 'metric_forks', 'metric_open_issues', 'metric_last_commit')
    list_filter = ('created_at', 'package')
    readonly_fields = ('created_at', 'metric_last_commit')


@admin.register(PackageTopic)
class PackageTopicAdmin(admin.ModelAdmin):
    list_display = ('package', 'name')
    search_fields = ['name']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'status')
    search_fields = ['name', 'email']
    list_filter = ('status', )


@admin.register(PackageRequest)
class PackageRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'submitted_at', 'is_approved']
    list_filter = ['is_approved']

    # Tight couple the Request Approval logic to the Admin UI only.
    def save_model(self, request, obj, form, change):
        if change and 'is_approved' in form.changed_data and obj.is_approved:
            try:
                obj.create_package_from_request()
            except ValidationError as e:
                messages.error(request, f"Error: {e.message}")
                obj.is_approved = False
                return
        super().save_model(request, obj, form, change)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'get_packages')

    def get_packages(self, obj):
        return ", ".join(package.slug for package in obj.packages.all())
    get_packages.short_description = 'Packages'