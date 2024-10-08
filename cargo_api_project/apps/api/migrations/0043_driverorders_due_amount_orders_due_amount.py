# Generated by Django 4.2.2 on 2024-06-13 01:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0042_driverorders_distance_orders_distance'),
    ]

    operations = [
        migrations.AddField(
            model_name='driverorders',
            name='due_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='orders',
            name='due_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
