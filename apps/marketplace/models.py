# apps/marketplace/models.py
from uuid import uuid4

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg, Q
from django.urls import reverse


def product_image_upload_to(instance, filename: str) -> str:
    """
    Store product images under products/<owner_id>/<uuid>.<ext>
    Uses UUID to avoid filename collisions and accidental overwrites.
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpg"
    owner = instance.owner_id or "anon"
    return f"products/{owner}/{uuid4().hex}.{ext}"


class Product(models.Model):
    # nullable owner so existing rows won’t demand a default during migrations
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to=product_image_upload_to, blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # useful for sorting/invalidating caches

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["active", "-created_at"]),
            models.Index(fields=["title"]),
        ]

    def __str__(self):
        return f"{self.title} (#{self.pk})"

    def get_absolute_url(self):
        return reverse("marketplace:product_detail", args=[self.pk])

    @property
    def rating_avg(self):
        return self.reviews.aggregate(avg=Avg("rating"))["avg"] or 0

    @property
    def rating_count(self):
        return self.reviews.count()


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1–5",
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            # one review per user per product
            models.UniqueConstraint(fields=["product", "user"], name="unique_user_review"),
            # DB-level guard for rating range (in addition to field validators)
            models.CheckConstraint(check=Q(rating__gte=1, rating__lte=5), name="rating_1_to_5"),
        ]

    def __str__(self):
        return f"Review p#{self.product_id} by u#{self.user_id} — {self.rating}★"
