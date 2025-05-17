#!/bin/bash
set -e

echo "=== Astronomy API Startup ==="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Directory contents: $(ls -la)"

# Create necessary directories
echo "Creating template directories..."
python create_dirs.py

# Run import test
echo "Testing imports..."
python test_imports.py

# Wait for database to be ready
echo "Waiting for database to be ready..."
host=$(echo $DATABASE_URL | sed -r 's/.*@([^:]+):.*/\1/' || echo "astronomy-db")
port=$(echo $DATABASE_URL | sed -r 's/.*:([0-9]+)\/.*/\1/' || echo "3306")

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
echo "Testing database connection..."
cat > test_db.py << 'EOF'
import os
import sys
print("DATABASE_URL:", os.environ.get('DATABASE_URL', 'Not set'))
try:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db = SQLAlchemy(app)
    
    with app.app_context():
        result = db.session.execute('SELECT 1').fetchone()
        print(f"Database connection successful! Test query result: {result}")
except Exception as e:
    print(f"Database connection error: {str(e)}")
    sys.exit(1)
EOF

python test_db.py

# Initialize and seed the database
echo "Initializing database..."
FLASK_APP=server.py python -m flask init-db || { echo "Database initialization failed"; exit 1; }

echo "Seeding database..."
FLASK_APP=server.py python -m flask seed-db || { echo "Database seeding failed"; exit 1; }

# Start the application with verbose debugging
echo "Starting the application..."
export PYTHONUNBUFFERED=1
echo "Environment variables:"
env | grep -v PASSWORD
export FLASK_DEBUG=1
export FLASK_ENV=development

# Run with gunicorn in debug mode
exec gunicorn --bind 0.0.0.0:5000 --log-level debug --access-logfile - --error-logfile - server:app
