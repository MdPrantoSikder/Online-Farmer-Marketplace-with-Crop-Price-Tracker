from django.urls import path
from . import views

app_name = "farmers"

urlpatterns = [
    path("all/", views.all_farmers, name="all_farmers"),
    path("profile/<int:farmer_id>/", views.farmer_profile, name="farmer_profile"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("create-product/", views.product_create, name="product_create"),  
    path("product/edit/<int:pk>/", views.product_update, name="product_edit"),  # Updated this line
    path("product/delete/<int:pk>/", views.product_delete, name="product_delete"),  
    # Updated this line
    path('update-product/<int:pk>/', views.product_update, name='product_update'), 
    
]
