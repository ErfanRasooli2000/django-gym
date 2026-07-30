from modules.wallet.models import Wallet

def create_wallet():
    return Wallet.objects.create()