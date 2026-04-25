from django.core.management.base import BaseCommand

from app.models import Book, Category, Electronics, Fashion, Product


class Command(BaseCommand):
    help = "Seed sample data for product service"

    def handle(self, *args, **options):
        books = Category.objects.get_or_create(name="Books")[0]
        electronics = Category.objects.get_or_create(name="Electronics")[0]
        fashion = Category.objects.get_or_create(name="Fashion")[0]

        book_product, _ = Product.objects.get_or_create(
            name="Django for APIs",
            defaults={"price": 29.99, "stock": 20, "category": books},
        )
        Book.objects.get_or_create(
            product=book_product,
            defaults={"author": "William S. Vincent", "publisher": "WelcomeToCode", "isbn": "9781735467221"},
        )

        electronic_product, _ = Product.objects.get_or_create(
            name="Laptop Pro 14",
            defaults={"price": 1299.0, "stock": 10, "category": electronics},
        )
        Electronics.objects.get_or_create(product=electronic_product, defaults={"brand": "TechBrand", "warranty": 24})

        fashion_product, _ = Product.objects.get_or_create(
            name="Classic Hoodie",
            defaults={"price": 49.5, "stock": 30, "category": fashion},
        )
        Fashion.objects.get_or_create(product=fashion_product, defaults={"size": "L", "color": "Black"})

        self.stdout.write(self.style.SUCCESS("Product seed data loaded"))

