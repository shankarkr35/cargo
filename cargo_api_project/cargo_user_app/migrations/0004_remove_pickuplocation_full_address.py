# Generated by Django 4.0.6 on 2023-06-09 10:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cargo_user_app', '0003_alter_pickuplocation_latitude_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pickuplocation',
            name='full_address',
        ),
    ]
