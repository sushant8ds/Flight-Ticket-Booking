#!/bin/sh
set -e

# run migrations and collectstatic (no input)
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# pass control to CMD (gunicorn)
exec "$@"
