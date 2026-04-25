from django.db import models


class Order(models.Model):
    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Paid", "Paid"),
        ("Cancelled", "Cancelled"),
        ("Shipping", "Shipping"),
        ("Completed", "Completed"),
    )

    user_id = models.IntegerField()
    total_price = models.FloatField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Pending")

    class Meta:
        db_table = "orders"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_id = models.IntegerField()
    quantity = models.IntegerField()

