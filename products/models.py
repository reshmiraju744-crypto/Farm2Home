from django.db import models
from farmers.models import FarmerProfile


class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    def __str__(self):
        return self.name


class Product(models.Model):
    farmer=models.ForeignKey(FarmerProfile, on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    description=models.TextField()
    price=models.DecimalField(max_digits=8,decimal_places=2)
    stock=models.PositiveIntegerField()
    image=models.ImageField(upload_to='product_images/', blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name



