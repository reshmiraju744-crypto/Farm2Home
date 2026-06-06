from django.db import models
from django.conf import settings
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES=(
        ('Pending','Pending'),
        ('Confirmed','Confirmed'),
        ('Delivered','Delivered'),
      )

    user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_price=models.DecimalField(max_digits=10,decimal_places=2)
    status=models.CharField(max_length=20, choices=STATUS_CHOICES,default='Pending')
    created_at=models.DateTimeField(auto_now_add=True)

    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    def __str__(self):
        return f"Order {self.id} -{self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"


class Address(models.Model):
    ADDRESS_TYPES = [
        ('Home', 'Home'),
        ('Work', 'Work'),
        ('Farm', 'Farm'),
        ('Parents', 'Parents'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    label = models.CharField(
        max_length=20,
        choices=ADDRESS_TYPES,
        default='Home'
    )

    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.label} - {self.full_name}"