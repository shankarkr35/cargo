# Generated by Django 4.2.2 on 2024-04-11 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0035_alter_driverorders_paymentid_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='driverorders',
            name='order_by',
            field=models.IntegerField(default=1, max_length=4),
        ),
        migrations.AddField(
            model_name='orders',
            name='order_by',
            field=models.IntegerField(default=1, max_length=4),
        ),
    ]
