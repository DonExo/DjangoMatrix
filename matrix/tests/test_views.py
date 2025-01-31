from django.conf import settings
from packaging.version import Version
from django.urls import reverse
import pytest
from matrix.models import Package, PackageRequest, PackageVersion, PackageTopic


@pytest.mark.django_db
class TestViews:
    def test_index_view(self, client):
        response = client.get(reverse('index'))
        assert response.status_code == 200
        assert 'python_versions' in response.context

    def test_package_search(self, client):
        Package.objects.create(name="Django Packages", slug="django-packages")
        Package.objects.create(name="Django Channels", slug="django-channels")
        response = client.get(reverse('package_search'), {'q': 'packages'})
        assert len(response.json()['results']) == 1
        assert response.json()['results'][0]['name'] == "Django Packages"

    def test_package_add_get(self, client):
        response = client.get(reverse('package_add'))
        assert response.status_code == 200
        assert 'form' in response.context

    def test_package_add_post_valid(self, client):
        data = {
            'name': 'New Package',
            'repository_url': 'https://github.com/owner/repo',
            'description': 'Test package',
            'latest_version': '1.0'
        }
        response = client.post(reverse('package_add'), data)
        assert PackageRequest.objects.count() == 1
        assert response.status_code == 302

    def test_package_details_view(self, client):
        pkg = Package.objects.create(name="Test Package", slug="test-package")
        response = client.get(reverse('package_details', args=[pkg.slug]))
        assert response.status_code == 200
        content = response.content.decode('utf-8')

        required_strings = [
            'Compatibility Matrix',
            'Description',
            'Links',
            'Data Metrics',
            'Tags (Topics)',
            'Additional Information',
            'Github Metrics Data',
            'Similar Packages'
        ]

        assert all(s in content for s in required_strings), f"Content missing one or more required strings"

    def test_package_details_displays_similar_packages(self, client):
        # Create main package with topics
        main_package = Package.objects.create(
            name="Django Main",
            slug="django-main",
            description="Main test package"
        )
        PackageTopic.objects.create(package=main_package, name="web")
        PackageTopic.objects.create(package=main_package, name="authentication")

        # Create similar packages
        similar_packages = [
            ("Django Environ", "Environment variables configuration"),
            ("DRF Spectacular", "OpenAPI schema generation"),
            ("Django Allauth", "Authentication integration"),
        ]

        for name, desc in similar_packages:
            pkg = Package.objects.create(name=name, description=desc)
            PackageTopic.objects.create(package=pkg, name="web")
            PackageTopic.objects.create(package=pkg, name="authentication")

        # Create a non-similar package
        unrelated = Package.objects.create(name="Unrelated Package", description="No connection")
        PackageTopic.objects.create(package=unrelated, name="graph")

        response = client.get(reverse('package_details', args=[main_package.slug]))
        content = response.content.decode()

        # Verify similar packages are displayed with their metadata
        for name, desc in similar_packages:
            assert name in content
            assert desc in content

        # Verify non-similar package is not shown
        assert "Unrelated Package" not in content
        expected_packages = len(response.context['similar_packages'])
        assert expected_packages == 3, f"Expected 3, found {expected_packages}"

    def test_package_list_pagination(self, client):
        # Create 15 packages
        for i in range(1, 16):
            Package.objects.create(
                name=f"Django Package {i}",
                description=f"Package description {i}",
            )

        url = reverse('packages')

        # Check first page with ?per_page=10
        response_page1 = client.get(url, {'page': 1, 'per_page': 10})
        assert response_page1.status_code == 200
        # Get the table's paginated data
        table = response_page1.context['table']
        page_obj = table.page
        assert len(page_obj.object_list) == 10  # Items per page
        assert 'package_list' in response_page1.context

        # Check second page
        response_page2 = client.get(url, {'page': 2, 'per_page': 10})
        assert response_page2.status_code == 200
        table = response_page2.context['table']
        page_obj = table.page
        assert len(page_obj.object_list) == 5
        assert 'package_list' in response_page1.context

        content_page1 = response_page1.content.decode()
        assert "next" in content_page1.lower(), "Expected 'next' pagination link on first page"

        content_page2 = response_page2.content.decode()
        assert "previous" in content_page2.lower(), "Expected 'previous' pagination link on second page"

        # Check first page with ?per_page=25
        response_page3 = client.get(url, {'page': 1, 'per_page': 25})
        assert response_page3.status_code == 200
        table = response_page3.context['table']
        page_obj = table.page
        assert len(page_obj.object_list) == 15
        assert 'package_list' in response_page3.context

        # Make sure pagination links are not shown, as there is only one page
        assert "pagination" not in response_page3.context, "Expected 'pagination' link not to be present"

    def test_version_sorting(self):
        pkg = Package.objects.create(name="Version Sorting")
        versions = ['1.0', '2.0a', '1.1', '2.0', '1.0rc']

        for v in versions:
            PackageVersion.objects.create(package=pkg, version=v)

        sorted_versions = sorted(
            pkg.versions.all(),
            key=lambda x: Version(x.version),
            reverse=True
        )
        assert [v.version for v in sorted_versions] == ['2.0', '2.0a', '1.1', '1.0', '1.0rc']

    def test_package_search_with_pagination(self, client):
        # Create 15 packages - 12 with "Django" in name, 3 without
        for i in range(1, 13):
            Package.objects.create(
                name=f"Django Package {i}",
                description=f"Django-related package {i}",
            )
        for i in range(1, 4):
            Package.objects.create(
                name=f"Flask Package {i}",
                description=f"Flask-related package {i}",
            )
        url = reverse('packages')

        # Test basic search (should find 12 Django packages)
        response = client.get(url, {'search': 'Django'})
        assert response.status_code == 200
        table = response.context['table']
        assert table.paginator.count == 12  # Total matching items
        assert len(table.page.object_list) == 12

        # Test search with per_page=10
        response_page1 = client.get(url, {'search': 'Django', 'page': 1, 'per_page': 10})
        table_page1 = response_page1.context['table']
        assert len(table_page1.page.object_list) == 10
        assert table_page1.page.has_next() is True

        response_page2 = client.get(url, {'search': 'Django', 'page': 2, 'per_page': 10})
        table_page2 = response_page2.context['table']
        assert len(table_page2.page.object_list) == 2
        assert table_page2.page.has_previous() is True

        # Test search with per_page=5
        response_page1_small = client.get(url, {'search': 'Django', 'page': 1, 'per_page': 5})
        table_page1_small = response_page1_small.context['table']
        assert len(table_page1_small.page.object_list) == 5
        assert table_page1_small.paginator.num_pages == 3

        # Test search with no results
        response_empty = client.get(url, {'search': 'NonExistentPackage'})
        table_empty = response_empty.context['table']
        assert table_empty.paginator.count == 0
        assert "No packages found" in response_empty.content.decode()

        # Test search preserves parameters in pagination links
        content = response_page1.content.decode()
        assert '?search=Django&amp;page=2&amp;per_page=10' in content  # Check encoded next link
        assert 'per_page=10' in content

        # Test mixed case search (if your search is case-insensitive)
        response_mixed_case = client.get(url, {'search': 'dJaNgO'})
        assert response_mixed_case.context['table'].paginator.count == 12

        # Test search with special characters
        Package.objects.create(name="Django-Special!", description="With special chars")
        response_special = client.get(url, {'search': 'Django-Special!'})
        assert response_special.context['table'].paginator.count == 1

        # Test search with pagination and filter clearing
        if 'search' in response_page1.context['filter'].form.data:
            clear_url = f"{url}?per_page=10"
            response_cleared = client.get(clear_url)
            assert response_cleared.context['table'].paginator.count == 16  # Default 15 + last special one
