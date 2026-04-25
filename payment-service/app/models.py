from django.db import models


class Payment(models.Model):
    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Success", "Success"),
        ("Failed", "Failed"),
    )

    order_id = models.IntegerField()
    amount = models.FloatField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Pending")

