# wallet/models.py
from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class Wallet(models.Model):
    #user = models.ForeignKey(User,on_delete=models.CASCADE,default="")
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'wallet'

    def __str__(self):
        return f'{self.user.email}\'s Wallet'

class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10)  # 'credit' or 'debit'
    balance = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    note = models.CharField(max_length=100,null=True)
    paymentId = models.CharField(max_length=250, blank=True, default="", null=True)
    paymentStatus = models.CharField(max_length=150, blank=True, default="", null=True) 
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transaction'

    def __str__(self):
        return f'{self.transaction_type} of {self.amount} at {self.timestamp}'
