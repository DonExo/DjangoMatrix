from datetime import timedelta

import django_tables2 as tables
from django.conf import settings
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Package


class PackageTable(tables.Table):
    row_number = tables.Column(empty_values=(), verbose_name="#", orderable=False)
    name = tables.Column(verbose_name="Name", orderable=False)
    get_latest_version = tables.Column(verbose_name="Latest Version", orderable=False)
    metric_stars = tables.Column(
        verbose_name='<i class="bi bi-star-fill text-warning"></i> &nbsp; Stars',
        accessor='metric_stars',
        attrs={"td": {"class": "text-center"}, "th": {"class": "text-center"}}
    )
    metric_forks = tables.Column(
        verbose_name='<i class="bi bi-git text-primary"></i> &nbsp; Forks',
        accessor='metric_forks',
        attrs={"td": {"class": "text-center"}, "th": {"class": "text-center"}}

    )
    metric_open_issues = tables.Column(
        verbose_name='<i class="bi bi-exclamation-circle text-danger"></i> &nbsp; Open Issues',
        accessor='metric_open_issues',
        attrs={"td": {"class": "text-center"}, "th": {"class": "text-center"}}

    )
    actions = tables.TemplateColumn(
        template_code="""
        <a href="{% url 'package_details' record.slug %}" class="btn btn-sm btn-outline-primary me-2">
            <i class="bi bi-eye"></i> View
        </a>
        <a href="{{ record.repository_url }}/fork" class="btn btn-sm btn-outline-secondary" target="_blank">
            <i class="bi bi-git"></i> Fork
        </a>
        """,
        verbose_name="Actions",
        orderable=False,
    )

    class Meta:
        model = Package
        order_by = "-metric_stars"
        fields = ("row_number", "name", "get_latest_version", "metric_stars", "metric_forks", "metric_open_issues")
        attrs = {
            "class": "table table-striped table-hover table-packages",
            "thead": {"class": "table-success"}
        }

    def render_row_number(self, record):
        return mark_safe(f"<b>{list(self.data).index(record) + 1}</b>")

    def render_name(self, record):
        name_html = format_html('<span><a style="text-decoration: none; color:inherit;" href="{}">{}</a> </span>', record.slug, record.name)

        # Add "Unmaintained" badge conditionally
        if record.metric_last_commit:
            three_years_ago = timezone.now() - timedelta(days=settings.DAYS_UNMAINTAINED)
            if record.metric_last_commit < three_years_ago:
                tooltip_html = format_html(
                    ' <span data-bs-toggle="tooltip" data-bs-placement="right" '
                    'title="This package hasn\'t been updated or maintained in over 3 years.">⚠️</span>'
                )
                return name_html + tooltip_html

        return name_html
