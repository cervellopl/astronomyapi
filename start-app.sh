#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for database to be ready..."
host=$(echo $DATABASE_URL | sed -r 's/.*@([^:]+):.*/\1/')
port=$(echo $DATABASE_URL | sed -r 's/.*:([0-9]+)\/.*/\1/')

echo "Checking connection to database at $host:$port..."
for i in {1..30}; do
  if nc -z $host $port; then
    echo "Database is ready!"
    break
  fi
  
  echo "Database is not ready yet (attempt: $i/30). Waiting..."
  sleep 2
  
  if [ $i -eq 30 ]; then
    echo "Could not connect to database after 30 attempts. Exiting."
    exit 1
  fi
done

# Create a simple test script to verify database connection
cat > test_db.py << EOF
from flask import Flask
from database import db, configure_db
import os

# Create a simple Flask app for testing
app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Test the connection
with app.app_context():
    result = db.session.execute('SELECT 1').fetchone()
    print(f"Database connection successful! Test query result: {result}")
EOF

# Run the test script to verify database connection
echo "Testing database connection..."
python test_db.py

# Initialize and seed the database
echo "Initializing database..."
FLASK_APP=server.py python -m flask init-db

echo "Seeding database..."
FLASK_APP=server.py python -m flask seed-db

# Start the application
echo "Starting the application..."
exec gunicorn --bind 0.0.0.0:5000 server:app --log-level info --access-logfile - --error-logfile -
