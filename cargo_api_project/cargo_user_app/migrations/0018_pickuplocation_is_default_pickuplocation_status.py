# Generated by Django 4.0.6 on 2023-07-03 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cargo_user_app', '0017_pickuplocation_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='pickuplocation',
            name='is_default',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pickuplocation',
            name='status',
            field=models.BooleanField(default=True),
        ),
    ]
