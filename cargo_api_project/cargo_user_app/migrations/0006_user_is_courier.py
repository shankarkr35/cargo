# Generated by Django 4.1.6 on 2023-06-26 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cargo_user_app', '0005_vehicle'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_courier',
            field=models.BooleanField(default=False),
        ),
    ]
