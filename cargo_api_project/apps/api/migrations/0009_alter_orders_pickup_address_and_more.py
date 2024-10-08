# Generated by Django 4.0.6 on 2023-07-10 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_rename_pickup_id_orders_pickup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='pickup_address',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='orders',
            name='pickup_latitude',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='orders',
            name='pickup_longitude',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
