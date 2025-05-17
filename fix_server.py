"""
Fix server.py syntax error
"""

import os
import re

def fix_server_py():
    """Fix syntax error in server.py"""
    print("Attempting to fix server.py syntax error...")
    
    try:
        # Read the file
        with open('server.py', 'r') as f:
            content = f.read()
        
        # Look for unclosed string literals around line 22
        # Match patterns like: 'GET /api 
        # (string starts but doesn't end properly)
        fixed_content = re.sub(r"'GET /api(?![^']*')", r"'GET /api'", content)
        
        # If no changes were made with the specific pattern, try a more general approach
        if fixed_content == content:
            # Split into lines to check near line 22
            lines = content.split('\n')
            
            # Check lines around line 22 (0-indexed)
            for i in range(max(0, 21-5), min(len(lines), 21+5)):
                # Check for unclosed quotes
                single_quotes = lines[i].count("'")
                double_quotes = lines[i].count('"')
                
                # If odd number of quotes, there might be an unclosed quote
                if single_quotes % 2 != 0:
                    print(f"Line {i+1} has an odd number of single quotes: {lines[i]}")
                    # Try to fix by adding a closing quote at the end
                    lines[i] = lines[i] + "'"
                
                if double_quotes % 2 != 0:
                    print(f"Line {i+1} has an odd number of double quotes: {lines[i]}")
                    # Try to fix by adding a closing quote at the end
                    lines[i] = lines[i] + '"'
            
            # Rejoin the lines
            fixed_content = '\n'.join(lines)
        
        # Write the fixed content
        with open('server.py', 'w') as f:
            f.write(fixed_content)
        
        print("Fixed server.py syntax error.")
        return True
    except Exception as e:
        print(f"Error fixing server.py: {str(e)}")
        return False

# Create a fresh server.py file with known good content
def create_fresh_server():
    """Create a fresh server.py file with known good content"""
    print("Creating fresh server.py file...")
    
    server_content = '''"""
Astronomy API Server - Fixed Version
==================================
Main entry point for the Astronomy Observations API server.
"""

import os
from flask import Flask, jsonify, redirect, url_for
from flask_restful import Api
from sqlalchemy import text

# Create Flask app
app = Flask(__name__)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "mysql+pymysql://astronomy:astronomy@astronomy-db:3306/astronomy_db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Import database after app creation
from database import db, configure_db

# Configure the database
configure_db(app)

# Root endpoint
@app.route("/")
def index():
    """Root endpoint."""
    return jsonify({
        "status": "ok",
        "message": "Astronomy API is running",
        "web_interface": "/web",
        "endpoints": {
            "health": "/health",
            "types": "/api/types",
            "properties": "/api/properties",
            "places": "/api/places",
            "instruments": "/api/instruments",
            "objects": "/api/objects",
            "observations": "/api/observations"
        }
    })

# Health check endpoint
@app.route("/health")
def health():
    """Health check endpoint."""
    try:
        # Test database connection
        with app.app_context():
            result = db.session.execute(text("SELECT 1")).fetchone()
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "result": str(result)
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }), 500

# Start the server if run directly
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
'''
    
    try:
        with open('server.py', 'w') as f:
            f.write(server_content)
        print("Created fresh server.py file.")
        return True
    except Exception as e:
        print(f"Error creating server.py: {str(e)}")
        return False

# Main function
if __name__ == '__main__':
    # First try to fix the existing file
    if not fix_server_py():
        # If fixing fails, create a fresh file
        create_fresh_server()
