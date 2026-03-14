#!/bin/bash

echo "Copying template files from host to container..."

# Check if templates directory exists on host
if [ -d "/mnt/user-data/uploads" ]; then
    echo "Host templates directory found"
fi

# Create template directories in container
mkdir -p /app/templates/objects
mkdir -p /app/templates/observations
mkdir -p /app/templates/instruments
mkdir -p /app/templates/places
mkdir -p /app/templates/types
mkdir -p /app/templates/properties

echo "Template directories created successfully"