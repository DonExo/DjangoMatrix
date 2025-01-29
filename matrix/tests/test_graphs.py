import pytest

from django.utils import timezone

from matrix.graphs import get_package_graph
from matrix.models import Package, PackageRepoStats


@pytest.mark.django_db
class TestGraphs:
    def test_empty_graph(self):
        pkg = Package.objects.create(name="No Stats")
        assert get_package_graph(pkg) is None

    def test_graph_generation(self):
        pkg = Package.objects.create(name="With Stats")

        # Create test data in chronological order
        stats_data = [
            (100, 10, 1),
            (200, 20, 2),
            (300, 30, 3)
        ]

        for stars, forks, issues in stats_data:
            PackageRepoStats.objects.create(
                package=pkg,
                metric_stars=stars,
                metric_forks=forks,
                metric_open_issues=issues,
                metric_last_commit=timezone.now()
            )

        graph_html = get_package_graph(pkg)
        assert '"mode":"lines+markers"' in graph_html
        assert '"y":[100,200,300]' in graph_html  # Stars should be increasing
        assert '"y":[10,20,30]' in graph_html  # Forks
        assert '"y":[1,2,3]' in graph_html  # Open issues

        # Verify labels and titles
        assert '"text":"Last 30 Days"' in graph_html
        assert '"name":"Stars"' in graph_html
        assert '"name":"Forks"' in graph_html
        assert '"name":"Open Issues"' in graph_html

        # Verify correct number of traces (3 subplots × 1 trace each)
        assert graph_html.count('"type":"scatter",') == 3
