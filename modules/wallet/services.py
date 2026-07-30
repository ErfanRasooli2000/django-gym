from django.db import transaction

from modules.wallet.models import Wallet

def create_wallet():
    return Wallet.objects.create()

def transfer_wallet(from_wallet , to_wallet , amount):
    with transaction.atomic():
        if from_wallet.balance < amount:
            pass
