"""
Create necessary directories for templates
"""

import os

# Create base template directory
os.makedirs('templates', exist_ok=True)

# Create entity-specific template directories
for directory in [
    'templates/objects', 
    'templates/observations', 
    'templates/instruments',
    'templates/places',
    'templates/types',
    'templates/properties'
]:
    os.makedirs(directory, exist_ok=True)

print("Created template directories successfully")
