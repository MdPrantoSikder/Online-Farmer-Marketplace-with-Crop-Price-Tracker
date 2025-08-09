# apps/marketplace/api/serializers.py
from rest_framework import serializers
from apps.marketplace.models import Product, Category, Review

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "title", "description", "price", "image_url", "category", "active", "created_at", "updated_at"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "product", "user", "rating", "comment", "created_at"]
        read_only_fields = ["user", "created_at"]
