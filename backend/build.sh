#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "--- Installing Dependencies ---"
# Install all Python dependencies including psycopg2 for Postgres
pip install -r requirements.txt

echo "--- Running Collectstatic ---"
# Collect static files (CSS/JS for Django Admin)
python manage.py collectstatic --no-input

echo "--- Applying Migrations to Neon DB ---"
# Apply database migrations to the external Neon database
python manage.py migrate

echo "--- Build Complete ---"