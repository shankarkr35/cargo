# Generated by Django 4.0.6 on 2023-07-13 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_alter_orders_vehicle_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='pickup_date',
            field=models.CharField(default='', max_length=120),
        ),
        migrations.AlterField(
            model_name='orders',
            name='pickup_time',
            field=models.CharField(default='', max_length=120),
        ),
    ]
