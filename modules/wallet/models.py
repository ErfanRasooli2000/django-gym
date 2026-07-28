from django.db import models

class Wallet(models.Model):
    balance = models.BigIntegerField(default=0)
    pass

