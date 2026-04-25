from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("user_id", models.IntegerField()),
                ("total_price", models.FloatField()),
                ("status", models.CharField(choices=[("Pending", "Pending"), ("Paid", "Paid"), ("Cancelled", "Cancelled"), ("Shipping", "Shipping"), ("Completed", "Completed")], default="Pending", max_length=50)),
            ],
            options={"db_table": "orders"},
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("product_id", models.IntegerField()),
                ("quantity", models.IntegerField()),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="app.order")),
            ],
        ),
    ]

