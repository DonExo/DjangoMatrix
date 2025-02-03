from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.views.generic import TemplateView

from matrixProject.settings import ADMIN_URL_PATH
from .sitemaps import PackageSitemap, StaticViewSitemap
from matrix.views import contact_view

sitemaps = {
    'packages': PackageSitemap(),
    'static': StaticViewSitemap(),
}


urlpatterns = [
    path(ADMIN_URL_PATH, admin.site.urls),
    path('', include('matrix.urls')),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('privacy/', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    path('contact/', contact_view, name='contact'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
