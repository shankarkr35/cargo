# Generated by Django 4.2.2 on 2024-05-21 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0041_alter_orders_order_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='driverorders',
            name='distance',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
        migrations.AddField(
            model_name='orders',
            name='distance',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
    ]
