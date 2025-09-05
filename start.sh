#!/bin/sh
set -e

# --- Wait for DB if host/port provided ---
if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
  echo "⏳ Waiting for database at $DB_HOST:$DB_PORT..."
  ok=0
  for i in $(seq 1 120); do
    if nc -z "$DB_HOST" "$DB_PORT" >/dev/null 2>&1; then
      echo "✅ Database reachable."
      ok=1
      break
    fi
    sleep 1
  done
  if [ "$ok" -ne 1 ]; then
    echo "❌ Database not reachable after 120s. Exiting."
    exit 1
  fi
fi

echo "🚀 Running migrations..."
python manage.py migrate --noinput

echo "🧱 Collecting static files..."
python manage.py collectstatic --noinput

echo "🦄 Starting Gunicorn..."
exec gunicorn -c gunicorn.conf.py
