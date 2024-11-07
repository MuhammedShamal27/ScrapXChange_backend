#!/bin/bash

echo "DB_HOST: $DB_HOST"
echo "DB_PORT: $DB_PORT"

# Function to wait for a service
wait_for_service() {
  local host=$1
  local port=$2
  local service_name=$3

  echo "Waiting for $service_name ($host:$port)..."
  until nc -z -v -w30 "$host" "$port"
  do
    echo "Waiting for $service_name connection..."
    sleep 5
  done
}

# Wait for PostgreSQL
wait_for_service "$DB_HOST" "$DB_PORT" "PostgreSQL"

# Wait for Redis
wait_for_service "redis" "6379" "Redis"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Determine the command to execute
if [ "$1" ]; then
    echo "Executing command: $@"
    exec "$@"
else
    # Start Daphne if no command is passed
    echo "Starting Daphne server..."
    exec daphne -b 0.0.0.0 -p 8000 backend.asgi:application
fi
