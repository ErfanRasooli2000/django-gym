from .enums import TransactionCategory , TransactionType
from django.db import models

class Wallet(models.Model):
    balance = models.BigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)


class TransactionIdempotencyKey(models.Model):
    idempotency_key = models.CharField(max_length=100 , unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Transaction(models.Model):

    wallet = models.ForeignKey(Wallet , on_delete=models.PROTECT , related_name="transactions")
    amount = models.BigIntegerField(default=0)
    category = models.CharField(choices=TransactionCategory.choices , max_length=15)
    type = models.CharField(choices=TransactionType.choices , max_length=15)
    idempotency = models.ForeignKey(TransactionIdempotencyKey , related_name="transactions" ,  on_delete=models.PROTECT, null=True)
    balance_before = models.BigIntegerField(default=0)
    balance_after = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
