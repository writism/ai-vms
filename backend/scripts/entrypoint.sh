#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Seeding admin user..."
python -m scripts.seed_admin || true

echo "Starting AI-VMS backend..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 "$@"
