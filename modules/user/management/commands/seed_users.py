import os
from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from modules.user.enums import Gender
from modules.wallet.models import Wallet

User = get_user_model()

# Wallets are always seeded empty: the ledger is the source of truth, so any
# starting balance must come from real transactions (see `seed_transactions`).
SEED_USERS = [
    ("ali_ahmadi", "09121234501", "ali.ahmadi@example.com", "Ali", "Ahmadi", Gender.MALE, date(1994, 3, 12)),
    ("sara_moradi", "09121234502", "sara.moradi@example.com", "Sara", "Moradi", Gender.FEMALE, date(1997, 7, 24)),
    ("reza_karimi", "09121234503", "reza.karimi@example.com", "Reza", "Karimi", Gender.MALE, date(1990, 11, 2)),
    ("niloofar_rad", "09121234504", "niloofar.rad@example.com", "Niloofar", "Rad", Gender.FEMALE, date(2000, 1, 30)),
    ("hossein_najafi", "09121234505", "hossein.najafi@example.com", "Hossein", "Najafi", Gender.MALE, date(1988, 5, 18)),
    ("mina_shakeri", "09121234506", "mina.shakeri@example.com", "Mina", "Shakeri", Gender.FEMALE, date(1996, 9, 9)),
    ("kaveh_soltani", "09121234507", "kaveh.soltani@example.com", "Kaveh", "Soltani", Gender.MALE, date(1992, 12, 21)),
    ("elham_bagheri", "09121234508", "elham.bagheri@example.com", "Elham", "Bagheri", Gender.FEMALE, date(1999, 4, 6)),
    ("amir_tavakoli", "09121234509", "amir.tavakoli@example.com", "Amir", "Tavakoli", Gender.OTHER, date(1995, 8, 14)),
    ("parisa_ghasemi", "09121234510", "parisa.ghasemi@example.com", "Parisa", "Ghasemi", Gender.FEMALE, date(1993, 2, 27)),
]

DEFAULT_PASSWORD = "password123"


class Command(BaseCommand):
    help = "Seed the database with sample users (each with its own wallet)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete the seeded users (and their wallets) before creating them again.",
        )
        parser.add_argument(
            "--password",
            default=DEFAULT_PASSWORD,
            help=f"Password given to every seeded user (default: {DEFAULT_PASSWORD}).",
        )

    @transaction.atomic
    def handle(self, *args, **options):

        app_mode = os.environ.get("APP_MODE")

        if app_mode is not None and app_mode == "production":
            print("Application is On Production")
            return None

        password = options["password"]
        phone_numbers = [row[1] for row in SEED_USERS]

        if options["flush"]:
            stale = User.objects.filter(phone_number__in=phone_numbers)
            wallet_ids = list(stale.exclude(wallet=None).values_list("wallet_id", flat=True))
            deleted, _ = stale.delete()
            Wallet.objects.filter(id__in=wallet_ids).delete()
            self.stdout.write(self.style.WARNING(f"Removed {deleted} existing seeded row(s)."))

        created_count = 0
        for username, phone, email, first, last, gender, birth_date in SEED_USERS:
            if User.objects.filter(phone_number=phone).exists():
                self.stdout.write(f"  skip   {phone} ({username}) - already exists")
                continue

            wallet = Wallet.objects.create(balance=0)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                phone_number=phone,
                first_name=first,
                last_name=last,
                gender=gender,
                birth_date=birth_date,
                wallet=wallet,
            )
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f"  create {phone} ({user.username}) - wallet #{wallet.id} (empty)"))

        self.stdout.write(
            self.style.SUCCESS(f"\nDone. {created_count} user(s) created, password: {password}")
        )
        self.stdout.write("Run `manage.py seed_transactions` to fund the wallets from a ledger.")
