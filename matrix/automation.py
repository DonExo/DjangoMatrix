import time

import requests

from .models import Package

from django.conf import settings


def get_repo_stars():
    """Fetch the number of stars for a GitHub repository and updates it in the system"""
    packages = Package.objects.all()
    for package in packages:
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
            stars_count = data.get("stargazers_count", 0)
            package.popularity_metric = stars_count
            package.save()
            print(f"Package {package.name} has now {stars_count} stars.")
        else:
            raise Exception(f"Failed to fetch repository info: {response.status_code} {response.reason}")

        time.sleep(1)
