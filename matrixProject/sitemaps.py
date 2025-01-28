from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from matrix.models import Package


class PackageSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Package.objects.all()

    def location(self, obj):
        return f"/packages/{obj.slug}/"


class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ['index', 'about', 'package_add']

    def location(self, item):
        return reverse(item)
