# Generated by Django 4.0.6 on 2023-07-15 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cargo_driver_app', '0012_driver_country_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driver',
            name='country_code',
            field=models.CharField(default='+965', max_length=4),
        ),
    ]
