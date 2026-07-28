from .enums import TransactionCategory , TransactionType
from django.db import models

class Wallet(models.Model):
    balance = models.BigIntegerField(default=0)
    pass

class Transaction(models.Model):

    wallet_id = models.OneToOneField(Wallet , on_delete=models.CASCADE)
    amount = models.BigIntegerField(default=0)
    category = models.TextChoices(choices=TransactionCategory.choices)
    type = models.CharField(choices=TransactionType.choices)
    balance_before = models.BigIntegerField(default=0)
    balance_after = models.BigIntegerField(default=0)
