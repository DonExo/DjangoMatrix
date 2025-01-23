from packaging.version import Version

from django.core.exceptions import ValidationError
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
    metric_last_commit = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-metric_stars', )

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_latest_version(self):
        versions = self.versions.all()
        if versions:
            # Sort versions using `packaging.version.Version`
            return max(versions, key=lambda v: Version(v.version))
        return "-"

    @property
    def get_last_updated(self):
        last_updated = None
        if self.repo_stats.exists():
            last_updated = self.repo_stats.latest('created_at').created_at
        return last_updated

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
    metric_last_commit = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Repo stats for {self.package.name}"

    class Meta:
        verbose_name_plural = "Package repo stats"
        ordering = ('-created_at', )


class PackageVersion(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='versions')
    version = models.CharField(max_length=10)
    release_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    django_compatibility = models.ManyToManyField(DjangoVersion, blank=True)
    python_compatibility = models.ManyToManyField(PythonVersion, blank=True)

    class Meta:
        ordering = ('-release_date', )
        constraints = [
            models.UniqueConstraint(fields=['package', 'version'], name='unique_package_version')
        ]

    def __str__(self):
        return self.version

    def verbose_name(self):
        return f"{self.package.name} v{self.version}"


class PackageRequest(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    repository_url = models.URLField()
    documentation_url = models.URLField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    latest_version = models.CharField(max_length=100, null=True)
    django_compatible_versions = models.ManyToManyField(
        DjangoVersion,
        blank=True,
        help_text='Select all the compatible versions of the package',
    )

    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Package Request: {self.name}"

    def create_package_from_request(self):
        print("create_package_from_request")
        slug = slugify(self.name)
        if Package.objects.filter(slug=slug).exists():
            raise ValidationError(f"Package {slug} already exists")
        package = Package.objects.create(
            name=self.name,
            description=self.description,
            repository_url=self.repository_url,
            documentation_url=self.documentation_url,
        )
        if self.django_compatible_versions:
            package_version = PackageVersion.objects.create(
                package=package,
                version=self.latest_version,
            )
            package_version.django_compatibility.set(self.django_compatible_versions.all())

        # Fetch and create topics/tags from the repo.
        PackageTopic.create_topics(package)


class PackageTopic(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='topics')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def verbose_name(self):
        return f"{self.package} -{self.name}"

    @classmethod
    def create_topics(cls, package):
        print("In create_topics")
        from matrix import automation
        automation.create_package_topics(package)


class Compatibility(models.Model):
    django_version = models.ForeignKey(DjangoVersion, on_delete=models.CASCADE, related_name="compatibilities")
    python_version = models.ForeignKey(PythonVersion, on_delete=models.CASCADE, related_name="compatibilities", null=True, blank=True)
    package = models.ForeignKey("Package", on_delete=models.CASCADE, null=True, blank=True)
    version = models.CharField(max_length=100, help_text=_("example: 3.2.5"), null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Compatibility"
        verbose_name_plural = "Compatibilities"

    def __str__(self):
        return f"{self.django_version} - {self.python_version}"
