# apps/farmers/urls.py
from django.urls import path
from . import views

app_name = "farmers"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("products/add/", views.product_create, name="product_add"),
    path("products/<int:pk>/edit/", views.product_update, name="product_edit"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),
]
