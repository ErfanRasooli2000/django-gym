from django.db import transaction, IntegrityError
from .enums import TransactionCategory , TransactionType
from modules.wallet.models import Wallet, Transaction
from .exceptions import LowWalletBalance, TransferFailed, ConflictIdempotencyKey
from .models import TransactionIdempotencyKey


def create_wallet():
    return Wallet.objects.create()


def transfer_wallet(from_wallet , to_wallet , amount , idempotency_key):

    if check_idempotency_key_exists(idempotency_key) is None:
        return None

    try:
        with transaction.atomic():
            ids = [from_wallet.id , to_wallet.id]
            locked = {
                w.id: w
                for w in Wallet.objects.select_for_update().filter(pk__in=ids).order_by("pk")
            }

            sender , receiver = locked[from_wallet.id], locked[to_wallet.id]

            idempotency = TransactionIdempotencyKey.objects.create(idempotency_key=idempotency_key , wallet = sender)
            create_transaction(sender , amount , TransactionType.DEBIT , TransactionCategory.TRANSFER , idempotency)
            create_transaction(receiver , amount , TransactionType.CREDIT , TransactionCategory.TRANSFER , idempotency)

    except IntegrityError:
        idempotencyKey = check_idempotency_key_exists(idempotency_key)
        if idempotencyKey is not None:
            if idempotencyKey.wallet.id == from_wallet.id:
                return None
            else:
                raise ConflictIdempotencyKey()

        raise TransferFailed()

    return None

def create_transaction(wallet: Wallet , amount: int , transaction_type: TransactionType , category: TransactionCategory , idempotency : TransactionIdempotencyKey):

    balance_before = wallet.balance
    balance_after = wallet.balance

    if transaction_type == TransactionType.DEBIT:
        if wallet.balance < amount:
            raise LowWalletBalance()

        balance_after -= amount
    else:
        balance_after += amount

    wallet.balance = balance_after
    wallet.save(update_fields=['balance'])

    Transaction.objects.create(wallet = wallet , amount = amount , category = category , type= transaction_type , balance_before = balance_before , balance_after = balance_after , idempotency = idempotency)


def check_idempotency_key_exists(key):
    return TransactionIdempotencyKey.objects.filter(idempotency_key=key).first()