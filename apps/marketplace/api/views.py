# apps/marketplace/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from apps.marketplace.models import Product, Review, Category
from .serializers import ProductSerializer, ReviewSerializer, CategorySerializer

@api_view(["GET"])
def api_products_list(request):
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("category")
    qs = Product.objects.filter(active=True)
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if cat:
        qs = qs.filter(category__slug=cat)

    paginator = PageNumberPagination()
    paginator.page_size = 12
    page = paginator.paginate_queryset(qs.order_by("-created_at"), request)
    serializer = ProductSerializer(page, many=True, context={"request": request})
    return paginator.get_paginated_response(serializer.data)

@api_view(["GET"])
def api_product_detail(request, pk):
    p = get_object_or_404(Product, pk=pk, active=True)
    serializer = ProductSerializer(p, context={"request": request})
    return Response(serializer.data)

@api_view(["GET"])
def api_categories(request):
    qs = Category.objects.all()
    serializer = CategorySerializer(qs, many=True)
    return Response(serializer.data)

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def api_reviews_for_product(request, pk):
    product = get_object_or_404(Product, pk=pk, active=True)
    if request.method == "GET":
        qs = Review.objects.filter(product=product).order_by("-created_at")
        serializer = ReviewSerializer(qs, many=True)
        return Response(serializer.data)
    # POST - create or update user's review
    data = request.data.copy()
    data["product"] = product.pk
    # enforce one review per user using update_or_create
    obj, created = Review.objects.update_or_create(
        product=product, user=request.user, defaults={"rating": data.get("rating", 5), "comment": data.get("comment", "")}
    )
    serializer = ReviewSerializer(obj)
    return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

@api_view(["GET", "POST"])
def api_cart(request):
    """
    Session-based cart endpoint.
    GET -> return current cart items (product details + qty).
    POST -> add item: {product: id, qty: N}
    """
    cart = request.session.get("cart", {})
    if request.method == "GET":
        items = []
        ids = [int(k) for k in cart.keys()] if cart else []
        products = Product.objects.filter(pk__in=ids)
        product_map = {p.pk: p for p in products}
        for pk_str, qty in cart.items():
            pk = int(pk_str)
            p = product_map.get(pk)
            if not p:
                continue
            serializer = ProductSerializer(p, context={"request": request})
            items.append({"product": serializer.data, "qty": int(qty)})
        return Response({"items": items})
    # POST: add to cart
    prod_id = request.data.get("product")
    qty = int(request.data.get("qty", 1) or 1)
    p = get_object_or_404(Product, pk=prod_id, active=True)
    cart[str(p.pk)] = cart.get(str(p.pk), 0) + qty
    request.session["cart"] = cart
    request.session.modified = True
    return Response({"message": "Added", "cart": cart})
