import pytest
from django.core.exceptions import ValidationError

from matrix.models import (
    DjangoVersion,
    PythonVersion,
    Package,
    PackageVersion,
    PackageRequest,
    Compatibility,
)


@pytest.mark.django_db
class TestCoreModels:
    def test_django_version_str(self):
        version = DjangoVersion.objects.create(version="4.2")
        assert str(version) == "4.2"
        assert version.verbose_name() == "Django v4.2"

    def test_python_version_ordering(self):
        py38 = PythonVersion.objects.create(version="3.8", release_date="2020-10-05")
        py39 = PythonVersion.objects.create(version="3.9", release_date="2021-10-04")
        assert list(PythonVersion.objects.all()) == [py39, py38]

    def test_package_slug_auto_generation(self):
        pkg = Package.objects.create(name="Awesome Package")
        assert pkg.slug == "awesome-package"

    def test_package_latest_version(self):
        pkg = Package.objects.create(name="Test Package")
        PackageVersion.objects.create(package=pkg, version="1.0")
        PackageVersion.objects.create(package=pkg, version="2.0")
        assert pkg.get_latest_version() == "2.0"

    def test_package_version_ordering(self):
        pkg = Package.objects.create(name="Version Test")
        v1 = PackageVersion.objects.create(package=pkg, version="1.0", release_date="2023-01-01")
        v2 = PackageVersion.objects.create(package=pkg, version="2.0", release_date="2023-02-01")
        assert list(pkg.versions.all()) == [v2, v1]

    def test_package_metric_formatting(self):
        pkg = Package.objects.create(name="Metrics", metric_stars=1500, metric_forks=2300)
        assert pkg.format_metric_stars == "1.5k"
        assert pkg.format_metric_forks == "2.3k"

    def test_package_request_approval(self, mocker):
        # Mock GitHub API calls
        mock_fetch = mocker.patch('matrix.automation.fetch_github_data')
        mock_fetch.return_value = {
            "topics": ["django", "testing"],
            "stargazers_count": 42,
            "forks_count": 10,
            "open_issues_count": 2,
            "commits": [{"commit": {"committer": {"date": "2023-01-01"}}}]
        }

        Package.objects.create(
            name="New Package",
            repository_url="https://github.com/owner/repo"
        )

        django_version = DjangoVersion.objects.create(version="4.2")
        request = PackageRequest.objects.create(
            name="New Package",
            repository_url="https://github.com/owner/repo",
            latest_version="1.0",
            is_approved=True
        )
        request.django_compatible_versions.add(django_version)

        # Should raise validation error due to existing package
        with pytest.raises(ValidationError) as excinfo:
            request.create_package_from_request()

        assert "Package new-package already exists" in str(excinfo.value)
        mock_fetch.assert_not_called()  # Shouldn't reach API calls

    def test_successful_package_creation(self, mocker):
        mock_fetch = mocker.patch('matrix.automation.fetch_github_data')
        mock_fetch.return_value = {
            "topics": ["django", "testing"],
            "stargazers_count": 100,
            "forks_count": 20,
            "open_issues_count": 5,
            "commits": [{"commit": {"committer": {"date": "2023-01-01"}}}]
        }

        django_version = DjangoVersion.objects.create(version="4.2")
        request = PackageRequest.objects.create(
            name="New Package",
            repository_url="https://github.com/owner/repo",
            description="Test package",
            latest_version="1.0",
            is_approved=True
        )
        request.django_compatible_versions.add(django_version)

        request.create_package_from_request()

        package = Package.objects.get(slug="new-package")
        assert package.versions.count() == 1
        assert package.topics.count() == 2
        mock_fetch.assert_called_once()

    def test_compatibility_model(self):
        django = DjangoVersion.objects.create(version="4.2")
        python = PythonVersion.objects.create(version="3.10")
        compat = Compatibility.objects.create(
            django_version=django,
            python_version=python,
            notes="Test compatibility"
        )
        assert str(compat) == "4.2 - 3.10"
