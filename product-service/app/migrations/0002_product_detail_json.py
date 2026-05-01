from django.db import migrations, models


def migrate_legacy_details(apps, schema_editor):
    Product = apps.get_model("app", "Product")
    Book = apps.get_model("app", "Book")
    Electronics = apps.get_model("app", "Electronics")
    Fashion = apps.get_model("app", "Fashion")

    for book in Book.objects.select_related("product"):
        Product.objects.filter(pk=book.product_id).update(
            detail_type="book",
            detail={
                "author": book.author,
                "publisher": book.publisher,
                "isbn": book.isbn,
            },
        )

    for electronics in Electronics.objects.select_related("product"):
        Product.objects.filter(pk=electronics.product_id).update(
            detail_type="electronics",
            detail={
                "brand": electronics.brand,
                "warranty_months": electronics.warranty,
                "model": "",
            },
        )

    for fashion in Fashion.objects.select_related("product"):
        Product.objects.filter(pk=fashion.product_id).update(
            detail_type="fashion",
            detail={
                "size": fashion.size,
                "color": fashion.color,
                "material": "",
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="detail",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="product",
            name="detail_type",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.RunPython(migrate_legacy_details, migrations.RunPython.noop),
        migrations.DeleteModel(name="Book"),
        migrations.DeleteModel(name="Electronics"),
        migrations.DeleteModel(name="Fashion"),
    ]
