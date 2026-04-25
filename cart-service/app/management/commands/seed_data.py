from django.core.management.base import BaseCommand

from app.models import Cart, CartItem


class Command(BaseCommand):
    help = "Seed sample data for cart service"

    def handle(self, *args, **options):
        cart, _ = Cart.objects.get_or_create(user_id=3)
        CartItem.objects.get_or_create(cart=cart, product_id=1, defaults={"quantity": 1})
        CartItem.objects.get_or_create(cart=cart, product_id=2, defaults={"quantity": 1})
        self.stdout.write(self.style.SUCCESS("Cart seed data loaded"))

