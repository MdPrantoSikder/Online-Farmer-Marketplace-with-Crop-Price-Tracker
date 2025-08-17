from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Product, Review
from .serializers import ProductSerializer, ReviewSerializer
from .models import Product
from django.shortcuts import get_object_or_404
class HomeApiView(APIView):
    """
    Home page with optional search
    """
    def get(self, request):
        q = request.GET.get("q", "").strip()
        products = Product.objects.filter(active=True)
        if q:
            products = products.filter(title__icontains=q)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductDetailApiView(APIView):
    """
    Retrieve, update, or delete a product.
    """
    def get(self, request, pk):
        # Retrieve the product
        product = Product.objects.filter(pk=pk, active=True).first()
        if not product:
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize the product data and return
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def delete(self, request, pk):
        # Retrieve the product to be deleted
        product = Product.objects.filter(pk=pk).first()
        if not product:
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Perform the deletion
        product.delete()
        
        # Return a success message
        return Response({"message": f"Product {pk} deleted."}, status=status.HTTP_204_NO_CONTENT)

        
class ProductListApiView(APIView):
    """
    API view to handle listing all products.
    """
    def get(self, request):
        products = Product.objects.filter(active=True)  # Only active products
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
        
class AddToCartApiView(APIView):
    """
    Add a product to the cart.
    """
    def post(self, request, pk):
        # Logic to add product to cart (just an example, actual cart logic needs to be handled)
        return Response({"message": f"Product {pk} added to cart"}, status=status.HTTP_200_OK)

class AddReviewApiView(APIView):
    """
    Add a review for a product.
    """
    def post(self, request, pk):
        product = Product.objects.filter(pk=pk).first()
        if not product:
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get data from the request
        rating = request.data.get('rating')
        comment = request.data.get('comment')

        if not rating or not comment:
            return Response({"detail": "Rating and comment are required"}, status=status.HTTP_400_BAD_REQUEST)

        review = Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment
        )
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)
