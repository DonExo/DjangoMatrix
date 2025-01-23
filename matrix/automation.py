import requests
import time
from urllib.parse import urlparse
from django.db import transaction
from django.conf import settings

from .models import PackageRepoStats, Package, PackageTopic


def fetch_github_data(url):
    """Helper function to fetch data from GitHub API."""
    headers = {
        "User-Agent": "DjangoMatrix/1.0 (https://djangomatrix.com)",
    }
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"GitHub API request failed: {response.status_code} {response.reason}")


def parse_github_url(repo_url):
    """Parse the GitHub repository URL and extract owner and repo."""
    GITHUB_API_URL = "https://api.github.com/repos"
    parsed = urlparse(repo_url.rstrip('/'))
    parts = parsed.path.strip('/').split('/')
    if len(parts) < 2:
        raise ValueError("Invalid GitHub repository URL.")
    owner = parts[-2]
    repo = parts[-1]
    return f"{GITHUB_API_URL}/{owner}/{repo}"


def create_package_topics(package):
    """
    Get (and set) topics for a given package.
    Since topics/tags don't change often, the idea is to be run only once at the beginning of creation of a Package.
    """
    api_url = parse_github_url(package.repository_url)
    repo_data = fetch_github_data(api_url)
    repo_topics = repo_data["topics"]
    topics = []
    for topic in repo_topics:
        topic_obj = PackageTopic(package=package, name=topic)
        topics.append(topic_obj)
    PackageTopic.objects.bulk_create(topics)


def get_repo_stats():
    """Fetch the metrics from GitHub for all the packages in the system and update them."""
    updates = []
    for package in Package.objects.all():
        try:
            api_url = parse_github_url(package.repository_url)
            commits_url = f"{api_url}/commits?page=1"

            repo_data = fetch_github_data(api_url)
            metrics = {
                "metric_stars": repo_data.get("stargazers_count", 0),
                "metric_forks": repo_data.get("forks_count", 0),
                "metric_open_issues": repo_data.get("open_issues_count", 0),
            }

            commits_data = fetch_github_data(commits_url)
            metrics["metric_last_commit"] = commits_data[0]["commit"]["committer"]["date"]

            updates.append((package, metrics))
            print(f"Fetched data for {package.name}")

        except Exception as e:
            print(f"Error processing {package.name}: {str(e)}")
            continue

        time.sleep(0.2)

    # Batch database updates
    with transaction.atomic():
        for package, metrics in updates:
            PackageRepoStats.objects.create(package=package, **metrics)
            Package.objects.filter(pk=package.pk).update(**metrics)

    print("All packages updated successfully!")
