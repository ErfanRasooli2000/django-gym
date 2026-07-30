from django.db import transaction

from modules.wallet.services import create_wallet
from .models import User

def register_user(data , password):
    with transaction.atomic():
        wallet = create_wallet()
        data['username'] = data["phone_number"]
        data['wallet'] = wallet
        user = User.objects.create_user(**data, password=password)
        return user
