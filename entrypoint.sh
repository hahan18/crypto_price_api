#!/bin/sh

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Start Daphne server
echo "Starting Daphne server..."
daphne -b 0.0.0.0 -p 8000 crypto_prices.asgi:application
