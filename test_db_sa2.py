"""
Test database connection with SQLAlchemy 2.0 compatibility
"""

import os
import sys

print("DATABASE_URL:", os.environ.get('DATABASE_URL', 'Not set'))

try:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy import text
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://astronomy:astronomy@astronomy-db:3306/astronomy_db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db = SQLAlchemy(app)
    
    with app.app_context():
        result = db.session.execute(text('SELECT 1')).fetchone()
        print(f"Database connection successful! Test query result: {result}")
        
        # Test creating a simple table
        db.session.execute(text('CREATE TABLE IF NOT EXISTS test_table (id INT PRIMARY KEY, name VARCHAR(255))'))
        print("Table creation successful")
        
        # Test inserting data
        db.session.execute(text('INSERT INTO test_table (id, name) VALUES (1, "test") ON DUPLICATE KEY UPDATE name="test"'))
        db.session.commit()
        print("Data insertion successful")
        
        # Test selecting data
        result = db.session.execute(text('SELECT * FROM test_table')).fetchall()
        print(f"Select query result: {result}")
        
except Exception as e:
    print(f"Database connection error: {str(e)}")
    traceback_info = sys.exc_info()
    import traceback
    traceback.print_exception(*traceback_info)
    sys.exit(1)
