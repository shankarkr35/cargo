# Generated by Django 4.0.6 on 2023-07-10 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_alter_orders_pickup_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='pickup_address',
            field=models.CharField(default='', max_length=250),
        ),
        migrations.AlterField(
            model_name='orders',
            name='pickup_latitude',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='orders',
            name='pickup_longitude',
            field=models.CharField(default='', max_length=50),
        ),
    ]
