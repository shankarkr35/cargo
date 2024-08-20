# Generated by Django 4.0.6 on 2023-06-09 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cargo_user_app', '0002_cargo_package_delete_package'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pickuplocation',
            name='latitude',
            field=models.DecimalField(decimal_places=6, default=1, max_digits=9),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='pickuplocation',
            name='longitude',
            field=models.DecimalField(decimal_places=6, default=1, max_digits=9),
            preserve_default=False,
        ),
    ]
