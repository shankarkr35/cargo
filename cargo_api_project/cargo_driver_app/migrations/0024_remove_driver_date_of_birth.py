# Generated by Django 4.0.6 on 2024-02-24 13:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cargo_driver_app', '0023_alter_driver_date_of_birth'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='driver',
            name='date_of_birth',
        ),
    ]
