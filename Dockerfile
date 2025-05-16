# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=server.py
ENV FLASK_ENV=production

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . .

# Create an entrypoint script
RUN echo '#!/bin/bash' > /app/entrypoint.sh && \
    echo 'set -e' >> /app/entrypoint.sh && \
    echo 'echo "Waiting for MySQL to be ready..."' >> /app/entrypoint.sh && \
    echo 'host=$(echo $DATABASE_URL | sed -r "s/.*@([^:]+):.*/\\1/")' >> /app/entrypoint.sh && \
    echo 'port=$(echo $DATABASE_URL | sed -r "s/.*:([0-9]+)\\/.*/\\1/")' >> /app/entrypoint.sh && \
    echo 'echo "Checking connection to MySQL at $host:$port..."' >> /app/entrypoint.sh && \
    echo 'for i in {1..30}; do' >> /app/entrypoint.sh && \
    echo '  nc -z $host $port && echo "MySQL is ready!" && break' >> /app/entrypoint.sh && \
    echo '  echo "MySQL is not ready yet (attempt: $i/30). Waiting..."' >> /app/entrypoint.sh && \
    echo '  sleep 2' >> /app/entrypoint.sh && \
    echo '  if [ $i -eq 30 ]; then' >> /app/entrypoint.sh && \
    echo '    echo "Could not connect to MySQL after 30 attempts. Exiting."' >> /app/entrypoint.sh && \
    echo '    exit 1' >> /app/entrypoint.sh && \
    echo '  fi' >> /app/entrypoint.sh && \
    echo 'done' >> /app/entrypoint.sh && \
    echo 'echo "Initializing database..."' >> /app/entrypoint.sh && \
    echo 'python -m flask init-db' >> /app/entrypoint.sh && \
    echo 'echo "Seeding database..."' >> /app/entrypoint.sh && \
    echo 'python -m flask seed-db' >> /app/entrypoint.sh && \
    echo 'echo "Starting the application..."' >> /app/entrypoint.sh && \
    echo 'exec gunicorn --bind 0.0.0.0:5000 server:app' >> /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Run the application with the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
