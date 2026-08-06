#!/usr/bin/env bash
set -euo pipefail

# Render's free tier has no Background Worker option, so the Celery worker
# runs alongside gunicorn in this same dyno instead of as a separate service.
# It goes to sleep with the dyno on idle and wakes back up with it - fine for
# a low-traffic personal project, not how you'd run this at real scale.
celery -A backend worker --loglevel=info --concurrency=2 &

# exec replaces the shell with gunicorn so it becomes the dyno's main
# process and Render can track its exit status / restart it on crash.
exec gunicorn backend.wsgi:application --bind 0.0.0.0:"${PORT:-8000}"
