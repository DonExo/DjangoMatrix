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
    popularity_metric = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ('-popularity_metric', )

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def format_popularity_metric(self):
        if self.popularity_metric >= 1000:
            return f"{round(self.popularity_metric / 1000, 1)}k"
        return str(self.popularity_metric)


class Compatibility(models.Model):
    django_version = models.ForeignKey(DjangoVersion, on_delete=models.CASCADE, related_name="compatibilities")
    python_version = models.ForeignKey(PythonVersion, on_delete=models.CASCADE, related_name="compatibilities")
    package = models.ForeignKey(Package, on_delete=models.CASCADE, null=True, blank=True)
    version = models.CharField(max_length=100, help_text=_("example: 3.2.5"), null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Compatibility"
        verbose_name_plural = "Compatibilities"

    def __str__(self):
        return f"{self.django_version} - {self.python_version}"

