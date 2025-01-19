import requests
import time
from urllib.parse import urlparse
from django.db import transaction
from django.conf import settings

from .models import PackageRepoStats, Package


def fetch_github_data(url, headers):
    """Helper function to fetch data from GitHub API."""
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"GitHub API request failed: {response.status_code} {response.reason}")


def parse_github_url(repo_url):
    """Parse the GitHub repository URL and extract owner and repo."""
    parsed = urlparse(repo_url.rstrip('/'))
    parts = parsed.path.strip('/').split('/')
    if len(parts) < 2:
        raise ValueError("Invalid GitHub repository URL.")
    return parts[-2], parts[-1]


def get_repo_stats():
    """Fetch the metrics from GitHub for all the packages in the system and update them."""
    headers = {
        "User-Agent": "DjangoMatrix/1.0 (https://djangomatrix.com)",
        "Cache-Control": "no-cache"
    }
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

    updates = []
    for package in Package.objects.all():
        try:
            owner, repo = parse_github_url(package.repository_url)
            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            commits_url = f"{api_url}/commits?page=1"

            # Fetch repository data
            repo_data = fetch_github_data(api_url, headers)
            metrics = {
                "metric_stars": repo_data.get("stargazers_count", 0),
                "metric_forks": repo_data.get("forks_count", 0),
                "metric_open_issues": repo_data.get("open_issues_count", 0),
            }

            # Fetch last commit data
            commits_data = fetch_github_data(commits_url, headers)
            metrics["metric_last_commit"] = commits_data[0]["commit"]["committer"]["date"]

            # Collect updates
            updates.append((package, metrics))
            print(f"Fetched data for {package.name}")

        except Exception as e:
            print(f"Error processing {package.name}: {str(e)}")
            continue

        # Respect GitHub API rate limits
        time.sleep(0.2)

    # Batch database updates
    with transaction.atomic():
        for package, metrics in updates:
            PackageRepoStats.objects.create(package=package, **metrics)
            Package.objects.filter(pk=package.pk).update(**metrics)

    print("All packages updated successfully!")
