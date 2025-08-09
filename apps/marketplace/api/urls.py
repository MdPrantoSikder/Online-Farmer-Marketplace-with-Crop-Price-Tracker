# apps/marketplace/api/urls.py
from django.urls import path
from . import views
from django.urls import path, include
urlpatterns = [
     
    path("products/", views.api_products_list, name="api_products"),
    path("products/<int:pk>/", views.api_product_detail, name="api_product_detail"),
    path("products/<int:pk>/reviews/", views.api_reviews_for_product, name="api_product_reviews"),
    path("categories/", views.api_categories, name="api_categories"),
    path("cart/", views.api_cart, name="api_cart"),
]
