# Generated by Django 4.1.6 on 2023-06-26 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profiles',
            name='user_type',
            field=models.CharField(choices=[('1', 'Admin'), ('2', 'Agent'), ('3', 'User')], max_length=10),
        ),
    ]
