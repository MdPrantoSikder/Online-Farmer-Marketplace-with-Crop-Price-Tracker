# apps/marketplace/views.py
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.views.decorators.http import require_http_methods

from .models import Product, Review


def home(request):
    """
    Home with optional ?q= search, latest products, and optional ?new=<id> highlight.
    """
    q = (request.GET.get("q") or "").strip()
    qs = Product.objects.filter(active=True)
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    products = qs.order_by("-id")[:12]

    # Highlight a newly created/edited product (e.g., after farmer redirect)
    new_id = request.GET.get("new")
    highlight_id = int(new_id) if (new_id and new_id.isdigit()) else None

    return render(
        request,
        "marketplace/home.html",
        {"products": products, "highlight_id": highlight_id, "q": q},
    )


def product_detail(request, pk):
    """
    Product page with reviews list.
    """
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
