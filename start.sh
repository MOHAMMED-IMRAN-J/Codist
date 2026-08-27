#!/usr/bin/env bash
# Start the celery worker in the background
celery -A codist worker --loglevel=info &

# Start the gunicorn web server in the foreground
gunicorn codist.wsgi:application --bind 0.0.0.0:$PORT
