# apps/farmers/views.py

from functools import wraps
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from apps.marketplace.models import Product
from apps.marketplace.forms import ProductForm
from django.contrib.auth.models import User

def is_farmer(user) -> bool:
    """
    Returns True if the user has a profile with role == 'FARMER'.
    Adjust if your role field is stored differently.
    """
    prof = getattr(user, "profile", None)
    return bool(prof and getattr(prof, "role", "") == "FARMER")


def farmer_required(view_func):
    """
    Ensures the user is authenticated AND has role FARMER.
    Redirects to login with ?next=... if anonymous,
    or to the customer dashboard if not a farmer.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            login_url = reverse("accounts:login")
            return redirect(f"{login_url}?next={request.get_full_path()}")
        if not is_farmer(request.user):
            messages.error(request, "Farmer access required.")
            return redirect("accounts:customer_dashboard")
        return view_func(request, *args, **kwargs)
    return _wrapped


@farmer_required
def dashboard(request):
    """
    Farmer dashboard: list their products with edit/delete links.
    """
    products = Product.objects.filter(owner=request.user).order_by("-id")
    return render(request, "farmers/dashboard.html", {"products": products})


@farmer_required
@require_http_methods(["GET", "POST"])
def product_create(request):
    """
    Create a product (with image upload).
    """
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        product = form.save(commit=False)
        product.owner = request.user
        product.save()
        messages.success(request, "Product added.")
        return redirect("farmers:dashboard")
    return render(request, "farmers/product_form.html", {"form": form, "mode": "create"})

@farmer_required
@require_http_methods(["GET", "POST"])
def product_update(request, pk):
    """
    Update a product (only if it belongs to the farmer).
    """
    product = get_object_or_404(Product, pk=pk, owner=request.user)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Product updated.")
        return redirect("farmers:dashboard")

    return render(request, "farmers/product_form.html", {"form": form, "mode": "edit", "product": product})

@farmer_required
@require_http_methods(["POST"])
def product_delete(request, pk):
    """
    Delete a product (only if it belongs to the farmer).
    """
    product = get_object_or_404(Product, pk=pk, owner=request.user)
    product.delete()
    messages.info(request, "Product deleted.")
    return redirect("farmers:dashboard")




def farmer_profile(request, farmer_id):
    """
    Show a specific farmer's profile and their products.
    """
    farmer = get_object_or_404(User, id=farmer_id, profile__role="FARMER")
    products = Product.objects.filter(owner=farmer)

    return render(request, "farmers/farmer_profile.html", {"farmer": farmer, "products": products})
@farmer_required
def product_edit(request, pk):
    """
    Edit an existing product.
    """
    product = get_object_or_404(Product, pk=pk, owner=request.user)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Product updated.")
        return redirect("farmers:dashboard")

    return render(request, "farmers/product_form.html", {"form": form, "mode": "edit", "product": product})




def all_farmers(request):
    letter = request.GET.get("letter", "").upper()
    search_query = request.GET.get("search", "")
    farmers = User.objects.filter(profile__role="FARMER")

    # Handle alphabet filter
    if letter:
        farmers = farmers.filter(username__istartswith=letter)

    # Handle search query
    if search_query:
        farmers = farmers.filter(username__icontains=search_query)

    # Add all farmers' data
    farmer_data = []
    for farmer in farmers:
        products = Product.objects.filter(owner=farmer)
        farmer_data.append({
            "farmer": farmer,
            "products": products
        })
    
    return render(request, "farmers/all_farmers.html", {"farmer_data": farmer_data})
