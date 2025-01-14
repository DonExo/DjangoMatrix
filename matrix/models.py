from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class DjangoVersion(models.Model):
    version = models.CharField(max_length=10, unique=True)
    release_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    end_of_life_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)

    class Meta:
        ordering = ('-release_date', )

    def __str__(self):
        return self.version

    def verbose_name(self):
        return f"Django v{self.version}"


class PythonVersion(models.Model):
    version = models.CharField(max_length=10, unique=True)
    release_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    end_of_life_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)  #

    class Meta:
        ordering = ('-release_date', )

    def __str__(self):
        return self.version

    def verbose_name(self):
        return f"Python v{self.version}"


class Package(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    repository_url = models.URLField(max_length=500, null=True, blank=True)
    documentation_url = models.URLField(max_length=500, null=True, blank=True)
    metric_stars = models.PositiveIntegerField(null=True, blank=True)
    metric_forks = models.PositiveIntegerField(null=True, blank=True)
    metric_open_issues = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ('-metric_stars', )

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def format_metric_stars(self):
        if self.metric_stars and self.metric_stars >= 1000:
            return f"{round(self.metric_stars / 1000, 1)}k"
        return str(self.metric_stars)

    @property
    def format_metric_forks(self):
        if self.metric_forks and self.metric_forks >= 1000:
            return f"{round(self.metric_forks / 1000, 1)}k"
        return str(self.metric_forks)


class PackageRepoStats(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='repo_stats')
    metric_stars = models.PositiveIntegerField(default=0)
    metric_forks = models.PositiveIntegerField(default=0)
    metric_open_issues = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Repo stats for {self.package.name}"

    class Meta:
        verbose_name_plural = "Package repo stats"


class PackageVersion(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    version = models.CharField(max_length=10, unique=True)
    release_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    django_compatibility = models.ManyToManyField(DjangoVersion, blank=True)
    python_compatibility = models.ManyToManyField(PythonVersion, blank=True)

    class Meta:
        ordering = ('-release_date', )

    def __str__(self):
        return self.version

    def verbose_name(self):
        return f"Package v{self.version}"

class Compatibility(models.Model):
    django_version = models.ForeignKey(DjangoVersion, on_delete=models.CASCADE, related_name="compatibilities")
    python_version = models.ForeignKey(PythonVersion, on_delete=models.CASCADE, related_name="compatibilities", null=True, blank=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, null=True, blank=True)
    version = models.CharField(max_length=100, help_text=_("example: 3.2.5"), null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Compatibility"
        verbose_name_plural = "Compatibilities"

    def __str__(self):
        return f"{self.django_version} - {self.python_version}"

