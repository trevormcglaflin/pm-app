# Generated by Django 4.2.5 on 2023-10-01 15:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("greta", "0003_transaction"),
    ]

    operations = [
        migrations.AddField(
            model_name="portfoliomanager",
            name="cash_basis",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
    ]
