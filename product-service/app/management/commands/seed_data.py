from django.core.management.base import BaseCommand

from app.models import Category, Product
from app.product_types import PRODUCT_TYPE_SCHEMAS


PRODUCT_SEEDS = [
    {
        "category": "Books",
        "products": [
            {
                "name": "Django for APIs",
                "price": 29.99,
                "stock": 20,
                "detail_type": "book",
                "detail": {"author": "William S. Vincent", "publisher": "WelcomeToCode", "isbn": "9781735467221"},
            },
            {
                "name": "Clean Architecture",
                "price": 34.5,
                "stock": 14,
                "detail_type": "book",
                "detail": {"author": "Robert C. Martin", "publisher": "Prentice Hall", "isbn": "9780134494166"},
            },
        ],
    },
    {
        "category": "Electronics",
        "products": [
            {
                "name": "Laptop Pro 14",
                "price": 1299.0,
                "stock": 10,
                "detail_type": "electronics",
                "detail": {"brand": "TechBrand", "warranty_months": 24, "model": "LP14-2026"},
            },
            {
                "name": "Noise Cancel Earbuds",
                "price": 149.0,
                "stock": 35,
                "detail_type": "electronics",
                "detail": {"brand": "SoundPeak", "warranty_months": 12, "model": "NC-E2"},
            },
        ],
    },
    {
        "category": "Fashion",
        "products": [
            {
                "name": "Classic Hoodie",
                "price": 49.5,
                "stock": 30,
                "detail_type": "fashion",
                "detail": {"size": "L", "color": "Black", "material": "Cotton"},
            }
        ],
    },
    {
        "category": "Home & Living",
        "products": [
            {
                "name": "Oak Coffee Table",
                "price": 219.0,
                "stock": 8,
                "detail_type": "home-living",
                "detail": {"material": "Oak Wood", "dimensions": "100x60x42 cm", "room": "Living Room"},
            }
        ],
    },
    {
        "category": "Beauty",
        "products": [
            {
                "name": "Hydrating Serum",
                "price": 27.0,
                "stock": 40,
                "detail_type": "beauty",
                "detail": {"brand": "GlowLab", "skin_type": "Dry", "volume_ml": 30},
            }
        ],
    },
    {
        "category": "Sports",
        "products": [
            {
                "name": "Training Basketball",
                "price": 39.0,
                "stock": 25,
                "detail_type": "sports",
                "detail": {"brand": "CourtMax", "sport": "Basketball", "level": "Training"},
            }
        ],
    },
    {
        "category": "Toys",
        "products": [
            {
                "name": "Explorer Robot Kit",
                "price": 59.0,
                "stock": 18,
                "detail_type": "toys",
                "detail": {"age_range": "8+", "material": "ABS Plastic", "battery_required": True},
            }
        ],
    },
    {
        "category": "Grocery",
        "products": [
            {
                "name": "Organic Granola",
                "price": 8.5,
                "stock": 60,
                "detail_type": "grocery",
                "detail": {"weight_grams": 500, "expiry_days": 180, "organic": True},
            }
        ],
    },
    {
        "category": "Office",
        "products": [
            {
                "name": "Marker Set Pro",
                "price": 15.0,
                "stock": 55,
                "detail_type": "office",
                "detail": {"brand": "WriteWell", "pack_size": 12, "color": "Mixed"},
            }
        ],
    },
    {
        "category": "Pet Supplies",
        "products": [
            {
                "name": "Dog Bowl Steel",
                "price": 18.0,
                "stock": 22,
                "detail_type": "pet-supplies",
                "detail": {"pet_type": "Dog", "size": "Medium", "weight_grams": 450},
            }
        ],
    },
]


class Command(BaseCommand):
    help = "Seed sample data for product service"

    def handle(self, *args, **options):
        for category_seed in PRODUCT_SEEDS:
            category, _ = Category.objects.get_or_create(name=category_seed["category"])

            for product_seed in category_seed["products"]:
                detail_type = product_seed["detail_type"]
                if detail_type not in PRODUCT_TYPE_SCHEMAS:
                    raise ValueError(f"Unknown detail_type in seed: {detail_type}")

                product, created = Product.objects.get_or_create(
                    name=product_seed["name"],
                    defaults={
                        "price": product_seed["price"],
                        "stock": product_seed["stock"],
                        "category": category,
                        "detail_type": detail_type,
                        "detail": product_seed["detail"],
                    },
                )
                if not created:
                    product.price = product_seed["price"]
                    product.stock = product_seed["stock"]
                    product.category = category
                    product.detail_type = detail_type
                    product.detail = product_seed["detail"]
                    product.save()

        self.stdout.write(self.style.SUCCESS("Product seed data loaded"))
