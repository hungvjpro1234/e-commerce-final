from django.core.management.base import BaseCommand

from app.models import Shipment


class Command(BaseCommand):
    help = "Seed sample data for shipping service"

    def handle(self, *args, **options):
        Shipment.objects.get_or_create(order_id=1, defaults={"address": "123 Demo Street", "status": "Shipping"})
        self.stdout.write(self.style.SUCCESS("Shipping seed data loaded"))

