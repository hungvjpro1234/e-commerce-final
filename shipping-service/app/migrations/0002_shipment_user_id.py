from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="shipment",
            name="user_id",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
