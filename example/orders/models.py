from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Product(models.Model):
    """
    Product model for storing product information
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    """
    Order model for storing order information
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    products = models.ManyToManyField(Product, through="OrderItem")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} - {self.customer.username}"

    def approve(self):
        """Mark order as approved"""
        self.status = "approved"
        self.approved_at = timezone.now()
        self.save(update_fields=["status", "approved_at", "updated_at"])


class OrderItem(models.Model):
    """
    OrderItem model for storing order items
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(
        max_digits=10, decimal_places=2
    )  # Price at the time of purchase

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        return self.price * self.quantity
