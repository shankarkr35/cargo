# Generated by Django 4.0.6 on 2023-07-20 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cargo_user_app', '0025_user_contract_file_user_courier_certificate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='droplocation',
            name='mobile',
            field=models.CharField(max_length=12, null=True),
        ),
    ]
