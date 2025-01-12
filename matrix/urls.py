from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("package/<slug:slug>/", views.package_details, name="package-details"),
]
