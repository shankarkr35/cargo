# Generated by Django 4.2.2 on 2024-06-14 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cargo_user_app', '0041_alter_user_branch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='address',
            field=models.CharField(max_length=250, null=True),
        ),
    ]
