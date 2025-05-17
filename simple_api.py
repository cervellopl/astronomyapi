"""
Simple API server with database connection
"""

import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://astronomy:astronomy@astronomy-db:3306/astronomy_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

@app.route('/')
def index():
    """Root endpoint."""
    return jsonify({
        'status': 'ok',
        'message': 'API server is running',
        'database_url': app.config['SQLALCHEMY_DATABASE_URI']
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    try:
        # Test database connection
        with app.app_context():
            result = db.session.execute(text('SELECT 1')).fetchone()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'result': str(result)
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
