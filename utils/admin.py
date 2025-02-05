from django.contrib import admin

from utils.models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('package', 'report_type', 'data', 'submitted_at')
    list_filter = ('report_type',)
    search_fields = ('package__name',)