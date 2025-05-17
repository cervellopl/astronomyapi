"""
Astronomy API Database Configuration
===================================
Database connection configuration for the Astronomy Observations API.

This module ensures proper database connection in various environments,
including Docker containers.
"""

import os
import time
import logging
from flask_sqlalchemy import SQLAlchemy

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize SQLAlchemy
db = SQLAlchemy()

def configure_db(app):
    """
    Configure database connection for the Flask application.
    
    Args:
        app: Flask application instance
    """
    # Get database URL from environment or use default
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        # Default for development
        database_url = 'mysql+pymysql://root:password@localhost/astronomy_db'
        logger.warning(f"DATABASE_URL not set, using default: {database_url}")
    else:
        logger.info(f"Using database URL: {database_url}")
    
    # Configure database connection
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database with app
    db.init_app(app)
    
    # Try to connect to the database
    with app.app_context():
        retries = 5
        while retries > 0:
            try:
                # Try to connect using SQLAlchemy 2.0 compatible syntax
                from sqlalchemy import text
                db.engine.connect()
                db.session.execute(text('SELECT 1'))
                logger.info("Successfully connected to database!")
                break
            except Exception as e:
                retries -= 1
                if retries == 0:
                    logger.error(f"Failed to connect to database: {str(e)}")
                    raise
                logger.warning(f"Could not connect to database, retrying in 5 seconds... ({retries} retries left)")
                logger.warning(f"Error: {str(e)}")
                time.sleep(5)
        
        # Create tables if they don't exist
        db.create_all()
        logger.info("Database tables created/verified.")
    
    return db
