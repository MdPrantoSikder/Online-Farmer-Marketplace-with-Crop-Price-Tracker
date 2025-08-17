# apps/marketplace/views.py
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.views.decorators.http import require_http_methods
from .models import Product, Review
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Product
from .serializers import ProductSerializer
from .models import Product, Wishlist


# In views.py
def home(request):
    q = (request.GET.get("q") or "").strip()
    qs = Product.objects.filter(active=True)
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    products = qs.order_by("-created_at")[:12]  # Get the latest 12 products

    return render(
        request,
        "marketplace/home.html",
        {"products": products},
    )



def product_detail(request, pk):
    """
    Product page with reviews list.
    """
    from .models import Product  # <-- Import Product inside the function to avoid circular import

    product = get_object_or_404(Product, pk=pk, active=True)
    reviews = (
        Review.objects.filter(product=product)
        .select_related("user")
        .order_by("-created_at")
    )
    return render(
        request,
        "marketplace/product_detail.html",
        {"product": product, "reviews": reviews},
    )
@login_required
@require_http_methods(["POST"])
def add_to_cart(request, pk):
    """
    Add a product to the session cart.
    """
    product = get_object_or_404(Product, pk=pk, active=True)

    # Check if the logged-in user is the owner (Farmer) of the product
    if product.owner == request.user:
        messages.error(request, "You cannot add your own product to the cart.")
        return redirect("marketplace:home")

    try:
        qty = int(request.POST.get("qty", 1))
    except (TypeError, ValueError):
        qty = 1
    qty = max(1, qty)

    cart = request.session.get("cart", {})
    cart[str(product.pk)] = cart.get(str(product.pk), 0) + qty
    request.session["cart"] = cart
    request.session.modified = True

    messages.success(request, f"Added {qty} × {product.title} to cart.")

    next_target = request.POST.get("next") or request.META.get("HTTP_REFERER") or "marketplace:view_cart"
    return redirect(resolve_url(next_target))


@login_required
def view_cart(request):
    """
    Show items currently in the session cart.
    """
    cart = request.session.get("cart", {})
    items = []
    total = Decimal("0.00")

    if cart:
        ids = [int(pk) for pk in cart.keys()]
        products = {p.pk: p for p in Product.objects.filter(pk__in=ids)}
        for pk_str, qty in cart.items():
            try:
                pk = int(pk_str)
                p = products.get(pk)
                if not p:
                    continue
                qty = int(qty)
                line = (p.price if isinstance(p.price, Decimal) else Decimal(str(p.price))) * qty
                total += line
                items.append({"product": p, "qty": qty, "line_total": line})
            except Exception:
                # Skip any malformed cart entry
                continue

    return render(request, "marketplace/cart.html", {"items": items, "total": total})


@login_required
@require_http_methods(["POST"])
def remove_from_cart(request, pk):
    cart = request.session.get("cart", {})
    if str(pk) in cart:
        del cart[str(pk)]
        request.session["cart"] = cart
        request.session.modified = True
        messages.info(request, "Item removed.")
    next_target = request.POST.get("next") or "marketplace:view_cart"
    return redirect(resolve_url(next_target))


@login_required
@require_http_methods(["POST"])
def clear_cart(request):
    request.session["cart"] = {}
    request.session.modified = True
    messages.info(request, "Cart cleared.")
    next_target = request.POST.get("next") or "marketplace:view_cart"
    return redirect(resolve_url(next_target))


@login_required
@require_http_methods(["POST"])
def add_review(request, pk):
    """
    Create or update a review for a product (one per user).
    """
    product = get_object_or_404(Product, pk=pk, active=True)

    try:
        rating = int(request.POST.get("rating", 5))
    except (TypeError, ValueError):
        rating = 5
    rating = max(1, min(5, rating))

    comment = (request.POST.get("comment") or "").strip()
    if not comment:
        messages.error(request, "Please write a comment.")
        return redirect("marketplace:product_detail", pk=product.pk)

    # Update existing review if it exists; otherwise create new
    with transaction.atomic():
        obj, created = Review.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={"rating": rating, "comment": comment},
        )

    messages.success(request, "Review saved." if not created else "Review added. Thanks!")
    return redirect("marketplace:product_detail", pk=product.pk)

class ProductSearchApiView(APIView):
    """
    API view to handle product search
    """
    def get(self, request):
        query = request.GET.get('q', '').strip()
        products = Product.objects.filter(active=True)
        
        if query:
            products = products.filter(Q(title__icontains=query) | Q(description__icontains=query))

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    

@login_required
def add_to_wishlist(request, pk):
    product = get_object_or_404(Product, pk=pk, active=True)
    # Check if the product is already in the wishlist
    if Wishlist.objects.filter(user=request.user, product=product).exists():
        messages.error(request, "Product already in your wishlist.")
    else:
        Wishlist.objects.create(user=request.user, product=product)
        messages.success(request, "Product added to your wishlist.")
    return redirect("marketplace:home")

@login_required
def remove_from_wishlist(request, pk):
    wishlist_item = get_object_or_404(Wishlist, user=request.user, product__pk=pk)
    wishlist_item.delete()
    messages.success(request, "Product removed from your wishlist.")
    return redirect("marketplace:home")


@login_required
def wishlist_view(request):
    # Get the current user's wishlist
    wishlist_items = Wishlist.objects.filter(user=request.user)

    return render(
        request,
        "marketplace/wishlist.html",  # Ensure this template exists
        {"wishlist_items": wishlist_items},
    )
