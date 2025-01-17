from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    path('', include('matrix.urls' )),
    path('admin/', admin.site.urls),
    path('sentry-debug/', trigger_error),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
