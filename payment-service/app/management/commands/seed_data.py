from django.core.management.base import BaseCommand

from app.models import Payment


class Command(BaseCommand):
    help = "Seed sample data for payment service"

    def handle(self, *args, **options):
        Payment.objects.get_or_create(order_id=1, amount=79.49, defaults={"status": "Success"})
        self.stdout.write(self.style.SUCCESS("Payment seed data loaded"))

