# Generated by Django 4.0.6 on 2023-07-28 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0031_remove_driverorders_device_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driverorders',
            name='device_token',
            field=models.CharField(max_length=220, null=True),
        ),
        migrations.AlterField(
            model_name='orders',
            name='device_token',
            field=models.CharField(max_length=220, null=True),
        ),
    ]
