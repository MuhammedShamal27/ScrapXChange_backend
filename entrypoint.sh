#!/bin/bash

# Wait for postgres
echo "Waiting for postgres..."
until nc -z -v -w30 $DB_HOST $DB_PORT
do
  echo "Waiting for database connection..."
  sleep 5
done

# Wait for redis
echo "Waiting for redis..."
until nc -z -v -w30 redis 6379
do
  echo "Waiting for redis connection..."
  sleep 5
done

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Start Daphne
exec daphne -b 0.0.0.0 -p 8000 backend.asgi:application