# Generated by Django 4.0.6 on 2023-07-07 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_remove_orders_driver_id_orders_driver'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='order_id',
            field=models.CharField(default='', max_length=250),
        ),
    ]
