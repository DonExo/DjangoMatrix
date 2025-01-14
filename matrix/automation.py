import time

import requests

from .models import Package, PackageRepoStats

from django.conf import settings


def get_repo_stars():
    """Fetch the metrics from GitHub for all the packages in the system and update it. """
    for package in Package.objects.all():
        try:
            parts = package.repository_url.rstrip('/').split('/')
            owner, repo = parts[-2], parts[-1]
        except IndexError:
            raise ValueError("Invalid GitHub repository URL.")

        api_url = f"https://api.github.com/repos/{owner}/{repo}"

        headers = {}
        if settings.GITHUB_TOKEN:
            headers['Authorization'] = f"token {settings.GITHUB_TOKEN}"

        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            metrics = {
                "metric_stars": data.get("stargazers_count", 0),
                "metric_forks": data.get("forks_count", 0),
                "metric_open_issues": data.get("open_issues_count", 0),
            }
            PackageRepoStats.objects.create(package=package, **metrics)
            Package.objects.filter(pk=package.pk).update(**metrics)
            print(f"Package {package.name} has now {metrics['metric_stars']} stars, {metrics['metric_forks']} forks and {metrics['metric_open_issues']} open issues.")
        else:
            raise Exception(f"Failed to fetch repository info: {response.status_code} {response.reason}")

        time.sleep(0.2)
