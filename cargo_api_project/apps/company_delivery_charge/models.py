from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from django.core.exceptions import ValidationError
from datetime import datetime

class CompanyDeliveryCharge(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE, default="", related_name='company_delivery_charges')
    #user = models.OneToOneField(User, on_delete=models.CASCADE)
    start_distance = models.PositiveIntegerField()
    end_distance = models.PositiveIntegerField()
    delivery_charge = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'company_delivery_charge'

    def clean(self):
        if self.start_distance >= self.end_distance:
            raise ValidationError({
                'start_distance': 'Start distance must be less than end distance.',
                'end_distance': 'End distance must be greater than start distance.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()  # Calls the clean method to perform validation
        super(CompanyDeliveryCharge, self).save(*args, **kwargs)
