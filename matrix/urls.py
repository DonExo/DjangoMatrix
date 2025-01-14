from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('packages/', views.packages, name='packages'),
    path('packages/search/', views.package_search, name='package_search'),
    path('packages/add/', views.package_add, name='package_add'),
    path('packages/<slug:slug>/', views.package_details, name='package_details'),
]
