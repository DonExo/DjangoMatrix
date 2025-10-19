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

        # Create test data across different weeks
        from datetime import timedelta
        base_date = timezone.now()

        stats_data = [
            (100, 10, 1, base_date - timedelta(weeks=2)),
            (200, 20, 2, base_date - timedelta(weeks=1)),
            (300, 30, 3, base_date)
        ]

        for stars, forks, issues, created_at in stats_data:
            stat = PackageRepoStats.objects.create(
                package=pkg,
                metric_stars=stars,
                metric_forks=forks,
                metric_open_issues=issues,
                metric_last_commit=created_at
            )
            stat.created_at = created_at
            stat.save()

        graph_html = get_package_graph(pkg)
        assert '"mode":"lines+markers"' in graph_html
        assert '"y":[100,200,300]' in graph_html  # Stars should be increasing
        assert '"y":[10,20,30]' in graph_html  # Forks
        assert '"y":[1,2,3]' in graph_html  # Open issues

        # Update title expectation
        assert '"text":"Last 9 Months (Weekly)"' in graph_html
        assert '"name":"Stars"' in graph_html
        assert '"name":"Forks"' in graph_html
        assert '"name":"Open Issues"' in graph_html

        # Verify correct number of traces (3 subplots × 1 trace each)
        assert graph_html.count('"type":"scatter",') == 3
