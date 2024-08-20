from django.db import models
from datetime import datetime

# Create your models here.
class DeliveryCharge(models.Model):
    delivery_charge = models.DecimalField(max_digits = 5,decimal_places = 2)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'delivery_charge'