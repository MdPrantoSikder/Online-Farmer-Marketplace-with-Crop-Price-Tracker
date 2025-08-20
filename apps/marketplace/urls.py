from django.urls import path
from . import views
from .views_api import HomeApiView, ProductDetailApiView, AddToCartApiView, AddReviewApiView
from .views import ProductSearchApiView  # Import your API view
from .views_api import ProductListApiView
app_name = "marketplace"

# Traditional Views
urlpatterns = [
    path("", views.home, name="home"),
    
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path("cart/", views.view_cart, name="view_cart"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:pk>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/clear/", views.clear_cart, name="clear_cart"),
    path("product/<int:pk>/review/", views.add_review, name="add_review"),
      path('wishlist/add/<int:pk>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    path('wishlist/remove/<int:pk>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    
]

# API Views
urlpatterns += [
    path("api/home/", HomeApiView.as_view(), name="home_api"),
     path('api/products/<int:pk>/', ProductDetailApiView.as_view(), name='product_detail_api'),
    path("api/cart/add/<int:pk>/", AddToCartApiView.as_view(), name="add_to_cart_api"),
    path("api/products/<int:pk>/review/", AddReviewApiView.as_view(), name="add_review_api"),
     path('api/products/search/', ProductSearchApiView.as_view(), name='product_search_api'),  # Add your new search API endpoint here
path('api/products/', ProductListApiView.as_view(), name='product_list_api'),

]
