from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()
    stock = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    detail_type = models.CharField(max_length=50, blank=True, default="")
    detail = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name
