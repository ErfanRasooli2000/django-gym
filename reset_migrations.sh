#!/usr/bin/env bash
#
# reset_migrations.sh — DEV ONLY
# Wipes all migrations + the database and regenerates everything from models.
# Do NOT run this against production. It drops your entire database.
#
set -euo pipefail

# Always run from the project root (dir this script lives in)
cd "$(dirname "$0")"

# --- Safety prompt -----------------------------------------------------------
read -r -p "This will DELETE all migrations and DROP the database. Continue? [y/N] " ans
case "$ans" in
  [yY][eE][sS]|[yY]) ;;
  *) echo "Aborted."; exit 1 ;;
esac

# --- Read the DB vars from .env WITHOUT shell expansion ----------------------
# We deliberately do NOT `source .env`: bash would expand a literal '$' inside a
# value (e.g. a password), but python-dotenv reads it literally. Parsing each
# key by hand keeps the value byte-for-byte identical to what Django sees.
if [[ ! -f .env ]]; then
  echo "Error: .env not found in $(pwd)"; exit 1
fi

get_env() {
  # Last matching key wins (mirrors dotenv). Strips optional surrounding quotes.
  local val
  val="$(grep -E "^${1}=" .env | tail -n1 | cut -d= -f2-)"
  val="${val%$'\r'}"                 # strip trailing CR if file has CRLF endings
  val="${val#[\"\']}"; val="${val%[\"\']}"  # strip one layer of surrounding quotes
  printf '%s' "$val"
}

DB_HOST="$(get_env DB_HOST)"
DB_PORT="$(get_env DB_PORT)"
DB_USER="$(get_env DB_USER)"
DB_PASSWORD="$(get_env DB_PASSWORD)"
DB_DATABASE="$(get_env DB_DATABASE)"

# --- 1. Delete migration files (keep every __init__.py) ----------------------
# IMPORTANT: only search project code (./modules). A bare `find .` would also
# match migration files INSIDE .venv (Django's own package) and destroy them.
echo "==> Deleting migration files..."
find ./modules -path '*/migrations/*.py' -not -name '__init__.py' -print -delete
find ./modules -path '*/migrations/*.pyc' -delete

# --- 2. Drop & recreate the MySQL database -----------------------------------
echo "==> Dropping and recreating database '${DB_DATABASE}'..."
mysql -h"${DB_HOST}" -P"${DB_PORT}" -u"${DB_USER}" -p"${DB_PASSWORD}" -e \
  "DROP DATABASE IF EXISTS \`${DB_DATABASE}\`; \
   CREATE DATABASE \`${DB_DATABASE}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# --- 3. Regenerate and apply migrations --------------------------------------
echo "==> Regenerating migrations..."
python manage.py makemigrations

echo "==> Applying migrations..."
python manage.py migrate

echo "==> seeding users..."
python manage.py seed_users

echo "==> seeding transactions..."
python manage.py seed_transactions