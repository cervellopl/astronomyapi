#!/bin/bash
# fix_sqlalchemy.sh - Script to fix SQLAlchemy 2.0 compatibility issues

echo "Fixing SQLAlchemy 2.0 compatibility issues..."

# Function to fix SQLAlchemy execute statements in a file
fix_file() {
    local file=$1
    echo "Checking file: $file"
    
    # Check if file exists
    if [ ! -f "$file" ]; then
        echo "File not found: $file"
        return
    fi
    
    # Check if file contains the pattern
    if grep -q "db.session.execute('SELECT" "$file"; then
        echo "Fixing db.session.execute statements in $file"
        sed -i "s/db.session.execute('SELECT/db.session.execute(text('SELECT/g" "$file"
        echo "File $file fixed."
    else
        echo "No issues found in $file."
    fi
}

# Fix specific files
fix_file "config.py"
fix_file "database.py"
fix_file "server.py"
fix_file "web_routes.py"

echo "SQLAlchemy compatibility fixes complete."
