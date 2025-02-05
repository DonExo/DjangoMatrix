from django.db import models

from matrix.models import Package


class Report(models.Model):
    REPORT_TYPES = [
        ('new_version', 'New Version'),
        ('update_version', 'Update Version'),
        ('irregularity', 'Irregularity'),
    ]

    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    data = models.JSONField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_report_type_display()} report at {self.submitted_at}"
