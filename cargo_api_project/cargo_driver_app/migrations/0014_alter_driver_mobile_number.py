# Generated by Django 4.0.6 on 2023-07-15 05:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cargo_driver_app', '0013_alter_driver_country_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driver',
            name='mobile_number',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
