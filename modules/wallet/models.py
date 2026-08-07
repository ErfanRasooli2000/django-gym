from modules.common.constraints import positive_constraint , enum_constraint
from modules.common.constraints import greater_than_zero_constraint
from modules.wallet.enums import TransactionCategory , TransactionType
from django.db import models

class Wallet(models.Model):
    class Meta:
        db_table = 'wallets'
        constraints = [
            positive_constraint(field_name="balance"),
        ]

    balance = models.BigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)


class TransactionIdempotencyKey(models.Model):

    class Meta:
        db_table = 'wallet_transaction_idempotency_key'
        indexes = [
            models.Index(fields=["wallet"] , name="wallet_index"),
        ]

    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name="idempotency_keys")
    idempotency_key = models.CharField(max_length=100 , unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Transaction(models.Model):

    class Meta:
        db_table = 'wallet_transactions'
        constraints = [
            greater_than_zero_constraint(field_name="amount"),
            positive_constraint(field_name="balance_after"),
            positive_constraint(field_name="balance_before"),
            enum_constraint(field_name="category" , types=TransactionCategory),
            enum_constraint(field_name="type" , types=TransactionType),
        ]
        indexes = [
            models.Index(fields=["wallet" , "-id"])
        ]

    wallet = models.ForeignKey(Wallet , on_delete=models.PROTECT , related_name="transactions")
    amount = models.IntegerField()
    category = models.CharField(choices=TransactionCategory , max_length=15)
    type = models.CharField(choices=TransactionType , max_length=15)
    idempotency = models.ForeignKey(TransactionIdempotencyKey , related_name="transactions" ,  on_delete=models.PROTECT, null=True)
    balance_before = models.IntegerField(default=0)
    balance_after = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
