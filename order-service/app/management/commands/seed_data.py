from django.core.management.base import BaseCommand

from app.models import Order, OrderItem


class Command(BaseCommand):
    help = "Seed sample data for order service"

    def handle(self, *args, **options):
        order, _ = Order.objects.get_or_create(user_id=3, total_price=79.49, status="Pending")
        OrderItem.objects.get_or_create(order=order, product_id=1, defaults={"quantity": 1})
        self.stdout.write(self.style.SUCCESS("Order seed data loaded"))

