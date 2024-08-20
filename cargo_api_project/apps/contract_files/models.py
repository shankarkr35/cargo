from django.db import models
from datetime import datetime 

# Create your models here.
class ContractFile(models.Model):
    contract_file = models.FileField(upload_to="contacts",default="")
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'contract_file'
       
