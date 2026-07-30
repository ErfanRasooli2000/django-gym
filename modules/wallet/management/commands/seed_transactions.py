import random

from django.core.management.base import BaseCommand
from django.db import transaction as db_transaction

from modules.wallet.enums import TransactionCategory, TransactionType
from modules.wallet.models import Transaction, Wallet

# Category buckets by direction.
DEBIT_CATEGORIES = [
    TransactionCategory.WITHDRAW,
    TransactionCategory.SUBSCRIPTION,
    TransactionCategory.TRANSFER,
]

STEP = 10_000           # every amount is a multiple of this
MIN_DEPOSIT = 50_000
MAX_DEPOSIT = 2_000_000


class Command(BaseCommand):
    help = "Seed a consistent transaction ledger for every wallet in the system."

    def add_arguments(self, parser):
        parser.add_argument(
            "--per-wallet",
            type=int,
            default=None,
            help="Fixed number of transactions per wallet (default: random 5-12).",
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing transactions before seeding.",
        )

    @db_transaction.atomic
    def handle(self, *args, **options):
        per_wallet = options["per_wallet"]

        if options["flush"]:
            deleted, _ = Transaction.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Removed {deleted} existing transaction(s)."))

        wallets = Wallet.objects.all()
        if not wallets:
            self.stdout.write(self.style.WARNING("No wallets found - nothing to seed."))
            return

        total_created = 0
        for wallet in wallets:
            count = per_wallet if per_wallet is not None else random.randint(5, 12)
            created = self._seed_wallet(wallet, count)
            total_created += created
            self.stdout.write(
                self.style.SUCCESS(
                    f"  wallet #{wallet.id}: {created} tx, final balance {wallet.balance:,}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. {total_created} transaction(s) created across {len(wallets)} wallet(s)."
            )
        )

    def _seed_wallet(self, wallet, count):
        """Build a forward-consistent ledger starting from 0 and sync the wallet balance."""
        running = 0
        rows = []
        for _ in range(count):
            # Force a deposit when there's nothing to spend, otherwise lean toward deposits.
            is_credit = running < MIN_DEPOSIT or random.random() < 0.55

            balance_before = running
            if is_credit:
                amount = random.randrange(MIN_DEPOSIT, MAX_DEPOSIT + STEP, STEP)
                running += amount
                category = TransactionCategory.DEPOSIT
                tx_type = TransactionType.CREDIT
            else:
                amount = random.randrange(STEP, running + STEP, STEP)  # never overspend
                running -= amount
                category = random.choice(DEBIT_CATEGORIES)
                tx_type = TransactionType.DEBIT

            rows.append(
                Transaction(
                    wallet=wallet,
                    amount=amount,
                    category=category,
                    type=tx_type,
                    balance_before=balance_before,
                    balance_after=running,
                )
            )

        Transaction.objects.bulk_create(rows)

        # Ledger is the source of truth: the wallet balance is the end of its history.
        wallet.balance = running
        wallet.save(update_fields=["balance"])
        return len(rows)
