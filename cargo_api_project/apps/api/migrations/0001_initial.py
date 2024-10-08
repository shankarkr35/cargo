# Generated by Django 4.0.6 on 2023-07-07 08:17

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cargo_driver_app', '0008_vehicle_status'),
        ('cargo_user_app', '0022_delete_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pickup_time', models.CharField(max_length=120)),
                ('pickup_address', models.CharField(max_length=250)),
                ('pickup_latitude', models.CharField(max_length=50)),
                ('pickup_longitude', models.CharField(max_length=50)),
                ('destination_address', models.CharField(max_length=250)),
                ('destination_latitude', models.CharField(max_length=50)),
                ('destination_longitude', models.CharField(max_length=50)),
                ('vehicle_type', models.CharField(max_length=120)),
                ('status', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('driver', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='cargo_driver_app.driver')),
                ('package', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='cargo_user_app.cargo_package')),
                ('user', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'order',
            },
        ),
    ]
