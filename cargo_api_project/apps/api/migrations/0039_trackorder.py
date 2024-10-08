# Generated by Django 4.2.2 on 2024-04-25 07:40

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cargo_driver_app', '0025_alter_driver_email'),
        ('api', '0038_alter_driverorders_vehicle_type_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrackOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_unique_id', models.CharField(default='', max_length=250)),
                ('status', models.IntegerField(default=1)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('driver', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cargo_driver_app.driver')),
                ('user', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'track_order',
            },
        ),
    ]
