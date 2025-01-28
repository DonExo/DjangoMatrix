from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from matrixProject.settings import ADMIN_URL_PATH

urlpatterns = [
    path('', include('matrix.urls')),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path(ADMIN_URL_PATH, admin.site.urls),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
