from django.db import models
from django.utils.translation import gettext_lazy as _

class TransactionCategory(models.TextChoices):
    DEPOSIT = "deposit", _("Deposit")
    WITHDRAW = "withdraw", _("Withdraw")
    TRANSFER = "transfer", _("Transfer")
    SUBSCRIPTION = "subscription", _("Subscription")

class TransactionType(models.TextChoices):
    CREDIT = "credit", _("Credit")
    DEBIT = "debit", _("Debit")