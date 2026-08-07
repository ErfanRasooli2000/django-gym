import os
import random
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction as db_transaction
from django.db.models import Max
from django.utils import timezone

from modules.wallet.enums import TransactionCategory, TransactionType
from modules.wallet.models import Transaction, Wallet

STEP = 10_000  # every amount is a multiple of this

# Amount rules per category, in STEP multiples.
DEPOSIT_RANGE = (50_000, 2_000_000)
WITHDRAW_RANGE = (50_000, 1_000_000)
TRANSFER_RANGE = (20_000, 500_000)
SUBSCRIPTION_PLANS = (300_000, 500_000, 900_000, 1_500_000)

# How the ledger leans. Deposits have to be frequent enough that wallets stay
# fundable, the rest is split between the ways money leaves a wallet.
P_DEPOSIT = 0.45
DEBIT_CATEGORIES = (
    TransactionCategory.WITHDRAW,
    TransactionCategory.SUBSCRIPTION,
    TransactionCategory.TRANSFER,
)
DEBIT_WEIGHTS = (0.35, 0.40, 0.25)

DEFAULT_TOTAL = 1_000
DEFAULT_WINDOW_DAYS = 180
BATCH_SIZE = 500


class Command(BaseCommand):
    help = "Seed a consistent transaction ledger for every wallet in the system."

    def add_arguments(self, parser):
        parser.add_argument(
            "--total",
            type=int,
            default=DEFAULT_TOTAL,
            help=f"Total transactions to spread over all wallets (default: {DEFAULT_TOTAL}).",
        )
        parser.add_argument(
            "--per-wallet",
            type=int,
            default=None,
            help="Fixed number of transactions per wallet. Overrides --total.",
        )
        parser.add_argument(
            "--days",
            type=int,
            default=DEFAULT_WINDOW_DAYS,
            help=f"Spread the ledger over the last N days (default: {DEFAULT_WINDOW_DAYS}).",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=None,
            help="Random seed, for a reproducible ledger.",
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing transactions before seeding.",
        )

    @db_transaction.atomic
    def handle(self, *args, **options):

        app_mode = os.environ.get("APP_MODE")

        if app_mode is not None and app_mode == "production":
            print("Application is On Production")
            return None

        if options["seed"] is not None:
            random.seed(options["seed"])

        if options["days"] < 1:
            raise CommandError("--days must be at least 1.")

        if options["flush"]:
            deleted, _ = Transaction.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Removed {deleted} existing transaction(s)."))

        wallets = list(Wallet.objects.order_by("id"))
        if not wallets:
            self.stdout.write(self.style.WARNING("No wallets found - nothing to seed."))
            return

        per_wallet = options["per_wallet"]
        if per_wallet is not None:
            if per_wallet < 0:
                raise CommandError("--per-wallet cannot be negative.")
            counts = [per_wallet] * len(wallets)
        else:
            if options["total"] < 0:
                raise CommandError("--total cannot be negative.")
            counts = self._random_split(options["total"], len(wallets))

        window_start = timezone.now() - timedelta(days=options["days"])

        total_created = 0
        for wallet, count in zip(wallets, counts):
            created = self._seed_wallet(wallet, count, window_start)
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

    def _random_split(self, total, buckets):
        """Spread `total` over `buckets` unevenly: a few heavy wallets, a long quiet tail.

        Pareto weights give the skew, largest-remainder rounding keeps the sum exact,
        and every wallet is guaranteed at least one transaction while there is budget.
        """
        if total <= buckets:
            return [1 if i < total else 0 for i in range(buckets)]

        remaining = total - buckets  # one transaction is reserved per wallet
        weights = [random.paretovariate(1.5) for _ in range(buckets)]
        scale = remaining / sum(weights)

        exact = [w * scale for w in weights]
        counts = [int(x) for x in exact]

        leftover = remaining - sum(counts)
        by_remainder = sorted(range(buckets), key=lambda i: exact[i] - counts[i], reverse=True)
        for i in by_remainder[:leftover]:
            counts[i] += 1

        return [c + 1 for c in counts]

    def _seed_wallet(self, wallet, count, window_start):
        """Build a forward-consistent ledger starting from 0 and charge the wallet with it."""
        if count == 0:
            wallet.balance = 0
            wallet.save(update_fields=["balance"])
            return 0

        # Sorted so the ledger reads chronologically in both id and created_at order.
        moments = sorted(self._random_moment(window_start) for _ in range(count))
        last_id = Transaction.objects.filter(wallet=wallet).aggregate(Max("id"))["id__max"] or 0

        running = 0
        rows = []
        for created_at in moments:
            balance_before = running
            category, tx_type, amount = self._random_entry(running)
            running += amount if tx_type == TransactionType.CREDIT else -amount

            rows.append(
                Transaction(
                    wallet=wallet,
                    amount=amount,
                    category=category,
                    type=tx_type,
                    balance_before=balance_before,
                    balance_after=running,
                    created_at=created_at,
                )
            )

        Transaction.objects.bulk_create(rows, batch_size=BATCH_SIZE)

        # created_at is auto_now_add, so the insert ignored our value - write it back.
        # MySQL does not return primary keys from a bulk insert, so re-read the rows
        # we just wrote: auto-increment ids follow insertion order, same as `moments`.
        inserted = list(
            Transaction.objects.filter(wallet=wallet, id__gt=last_id).order_by("id")
        )
        for row, created_at in zip(inserted, moments):
            row.created_at = created_at
        Transaction.objects.bulk_update(inserted, ["created_at"], batch_size=BATCH_SIZE)

        # Ledger is the source of truth: the wallet balance is the end of its history.
        wallet.balance = running
        wallet.save(update_fields=["balance"])
        return len(rows)

    def _random_entry(self, running):
        """Pick the next ledger entry. Never spends money the wallet does not have."""
        if random.random() >= P_DEPOSIT:
            category = random.choices(DEBIT_CATEGORIES, weights=DEBIT_WEIGHTS, k=1)[0]
            amount = self._debit_amount(category, running)
            if amount:
                return category, TransactionType.DEBIT, amount
            # Nothing affordable in that category - top the wallet up instead.

        return (
            TransactionCategory.DEPOSIT,
            TransactionType.CREDIT,
            self._step_amount(*DEPOSIT_RANGE),
        )

    def _debit_amount(self, category, running):
        """Largest allowed amount for `category`, or None when the wallet cannot cover it."""
        spendable = running - (running % STEP)

        if category == TransactionCategory.SUBSCRIPTION:
            affordable = [plan for plan in SUBSCRIPTION_PLANS if plan <= spendable]
            return random.choice(affordable) if affordable else None

        low, high = WITHDRAW_RANGE if category == TransactionCategory.WITHDRAW else TRANSFER_RANGE
        if spendable < low:
            return None
        return self._step_amount(low, min(high, spendable))

    @staticmethod
    def _step_amount(low, high):
        return random.randrange(low, high + STEP, STEP)

    @staticmethod
    def _random_moment(window_start):
        elapsed = timezone.now() - window_start
        return window_start + timedelta(seconds=random.uniform(0, elapsed.total_seconds()))
