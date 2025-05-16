#!/bin/bash
set -e

# Function to check if MySQL is ready
function wait_for_mysql() {
  echo "Waiting for MySQL to be ready..."
  
  host=$(echo $DATABASE_URL | sed -r 's/.*@([^:]+):.*/\1/')
  port=$(echo $DATABASE_URL | sed -r 's/.*:([0-9]+)\/.*/\1/')
  
  echo "Checking connection to MySQL at $host:$port..."
  
  for i in {1..30}; do
    nc -z $host $port && echo "MySQL is ready!" && return 0
    echo "MySQL is not ready yet (attempt: $i/30). Waiting..."
    sleep 2
  done
  
  echo "Could not connect to MySQL after 30 attempts. Exiting."
  exit 1
}

# Wait for MySQL to be ready
wait_for_mysql

# Initialize the database
echo "Initializing database..."
python -m flask init-db

# Seed the database
echo "Seeding database..."
python -m flask seed-db

# Start the application
echo "Starting the application..."
exec gunicorn --bind 0.0.0.0:5000 server:app
