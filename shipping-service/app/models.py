from django.db import models


class Shipment(models.Model):
    STATUS_CHOICES = (
        ("Processing", "Processing"),
        ("Shipping", "Shipping"),
        ("Delivered", "Delivered"),
    )

    order_id = models.IntegerField()
    user_id = models.IntegerField()
    address = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Processing")
