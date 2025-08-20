from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Product, Review
from .serializers import ProductSerializer, ReviewSerializer
from .models import Product
from django.shortcuts import get_object_or_404
from rest_framework import generics




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
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        product = Product.objects.filter(pk=pk, active=True).first()
        if not product:
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        # Full update (replace all fields)
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        # Partial update (only the given fields)
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = Product.objects.filter(pk=pk).first()
        if not product:
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        product.delete()
        return Response({"message": f"Product {pk} deleted."}, status=status.HTTP_204_NO_CONTENT)
class ProductCreateApiView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save(owner=request.user)
            return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        
class ProductListApiView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

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
