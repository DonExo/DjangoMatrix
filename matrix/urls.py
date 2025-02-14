from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('packages/', views.PackageListView.as_view(), name='packages'),
    path('packages/search/', views.package_search, name='package_search'),
    path('packages/submit/', views.package_add, name='package_add'),
    path('packages/<slug:slug>/', views.package_details, name='package_details'),
]


handler404 = 'matrix.views.custom_404'
handler500 = 'matrix.views.custom_500'
