# Generated by Django 4.0.6 on 2023-07-11 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cargo_driver_app', '0009_vehicletype_alter_vehicle_vehicle_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicletype',
            name='image',
            field=models.FileField(default='', upload_to='vehicle'),
        ),
    ]
