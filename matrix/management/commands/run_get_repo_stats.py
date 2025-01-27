from django.core.cache import cache

from django.core.management.base import BaseCommand
from matrix.automation import get_repo_stats


class Command(BaseCommand):
    help = 'Run get_repo_stats to collect repository stats'

    def handle(self, *args, **kwargs):
        self.stdout.write("Running get_repo_stats...")
        get_repo_stats()
        self.stdout.write("Completed get_repo_stats!")
        cache.clear()
        self.stdout.write("Cleaned up Cache memory.")
