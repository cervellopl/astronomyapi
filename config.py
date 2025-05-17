"""
Astronomy API Configuration
==========================
Configuration and setup utilities for the Astronomy Observations API.

This module provides:
- Database connection configuration
- Flask application configuration
- Schema initialization
- Example data loading
"""

import os
import json
from datetime import datetime
from flask import Flask, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
import click

# Import the database
from database import db, configure_db

# Load environment variables from .env file if present
load_dotenv()

# Initialize Flask application
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)


# ===============================================================================
# Configuration
# ===============================================================================

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'astronomy-api-dev-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'mysql+pymysql://root:password@localhost/astronomy_dev'
    )


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL', 
        'mysql+pymysql://root:password@localhost/astronomy_test'
    )


class ProductionConfig(Config):
    """Production configuration."""
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'mysql+pymysql://username:password@localhost/astronomy_prod'
    )


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def configure_app(flask_app, config_name=None):
    """
    Configure the Flask application.
    
    Args:
        flask_app: Flask application instance
        config_name: Configuration name ('development', 'testing', 'production')
    """
    config_name = config_name or os.environ.get('FLASK_CONFIG', 'default')
    flask_app.config.from_object(config[config_name])
    
    return flask_app


# Configure the application
app = configure_app(app)

# Configure database
db_instance = configure_db(app)


# ===============================================================================
# Database Management Commands
# ===============================================================================

@app.cli.command("init-db")
def init_db():
    """Initialize the database tables."""
    with app.app_context():
        db.create_all()
    click.echo("Database tables created.")


@app.cli.command("drop-db")
def drop_db():
    """Drop all database tables."""
    with app.app_context():
        db.drop_all()
    click.echo("Database tables dropped.")


@app.cli.command("recreate-db")
def recreate_db():
    """Recreate database tables."""
    with app.app_context():
        db.drop_all()
        db.create_all()
    click.echo("Database tables recreated.")


@app.cli.command("seed-db")
def seed_db():
    """Seed the database with initial data."""
    # Import models here to avoid circular imports
    from models import Type, Property, Place, Instrument, Object, Observation
    
    with app.app_context():
        # Create object types
        types = [
            Type(id=1, name="Galaxy"),
            Type(id=2, name="Star"),
            Type(id=3, name="Planet"),
            Type(id=4, name="Nebula"),
            Type(id=5, name="Asteroid")
        ]
        
        for type_obj in types:
            db.session.add(type_obj)
        
        # Create properties
        properties = [
            Property(id=1, name="Magnitude", valueType="float"),
            Property(id=2, name="Distance", valueType="string"),
            Property(id=3, name="Temperature", valueType="float"),
            Property(id=4, name="Diameter", valueType="string")
        ]
        
        for prop in properties:
            db.session.add(prop)
        
        # Create observation places
        places = [
            Place(
                id=1, 
                name="Royal Observatory Greenwich", 
                lat="51.4778", 
                lon="0.0015",
                alt="45m",
                timezone="Europe/London"
            ),
            Place(
                id=2, 
                name="Mauna Kea Observatory", 
                lat="19.8208", 
                lon="-155.4681",
                alt="4205m",
                timezone="Pacific/Honolulu"
            ),
            Place(
                id=3, 
                name="European Southern Observatory", 
                lat="-24.6275", 
                lon="-70.4044",
                alt="2635m",
                timezone="America/Santiago"
            )
        ]
        
        for place in places:
            db.session.add(place)
        
        # Create instruments
        instruments = [
            Instrument(
                id=1,
                name="Celestron NexStar 8SE", 
                aperture="203.2mm", 
                power="2032mm"
            ),
            Instrument(
                id=2,
                name="Subaru Telescope", 
                aperture="8.2m", 
                power="Primary f/1.83, Final f/12.2"
            ),
            Instrument(
                id=3,
                name="Very Large Telescope", 
                aperture="8.2m", 
                power="f/15"
            )
        ]
        
        for instrument in instruments:
            db.session.add(instrument)
        
        # Create celestial objects
        objects = [
            Object(
                id=1,
                name="Andromeda Galaxy",
                desination="M31",
                type=1,
                props=json.dumps({
                    "distance": "2.537 million light years",
                    "diameter": "220,000 light years",
                    "constellation": "Andromeda"
                })
            ),
            Object(
                id=2,
                name="Mars",
                desination="Sol d",
                type=3,
                props=json.dumps({
                    "distance": "227.9 million km from Sun",
                    "diameter": "6,779 km",
                    "moons": 2
                })
            ),
            Object(
                id=3,
                name="Orion Nebula",
                desination="M42",
                type=4,
                props=json.dumps({
                    "distance": "1,344 light years",
                    "diameter": "24 light years",
                    "constellation": "Orion"
                })
            )
        ]
        
        for obj in objects:
            db.session.add(obj)
        
        # Create sample observations
        observations = [
            Observation(
                object=1,  # Andromeda
                place=1,   # Greenwich
                instrument=1,  # Celestron
                datetime=datetime.utcnow(),
                observation="Clear spiral structure visible. Excellent seeing conditions.",
                prop1=1,  # Magnitude property
                prop1value="3.4"
            ),
            Observation(
                object=2,  # Mars
                place=2,   # Mauna Kea
                instrument=2,  # Subaru
                datetime=datetime.utcnow(),
                observation="Detailed surface features and polar ice caps visible.",
                prop1=2,  # Distance property
                prop1value="78.34 million km"
            ),
            Observation(
                object=3,  # Orion Nebula
                place=3,   # ESO
                instrument=3,  # VLT
                datetime=datetime.utcnow(),
                observation="High-resolution imaging of the trapezium cluster.",
                prop1=1,  # Magnitude property
                prop1value="4.0"
            )
        ]
        
        for observation in observations:
            db.session.add(observation)
        
        # Commit changes
        db.session.commit()
        
        click.echo("Database seeded with sample data.")


# ===============================================================================
# Health Check Endpoint
# ===============================================================================

@app.route('/health')
def health_check():
    """Health check endpoint for the API."""
    try:
        # Check database connection
        with app.app_context():
            db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'version': '1.0.0'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500


# ===============================================================================
# Server Configuration
# ===============================================================================

def run_server(host='0.0.0.0', port=5000, debug=True):
    """
    Run the Flask server.
    
    Args:
        host (str): Host address
        port (int): Port number
        debug (bool): Debug mode flag
    """
    app.run(host=host, port=port, debug=debug)


# ===============================================================================
# Main Entry Point
# ===============================================================================

if __name__ == '__main__':
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Run the Astronomy Observations API server')
    parser.add_argument('--host', '-H', default='0.0.0.0', help='Host address to bind to')
    parser.add_argument('--port', '-p', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--env', '-e', choices=['development', 'testing', 'production'], 
                        default='development', help='Environment configuration to use')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug mode')
    parser.add_argument('--init-db', action='store_true', help='Initialize database tables')
    parser.add_argument('--seed-db', action='store_true', help='Seed database with sample data')
    
    args = parser.parse_args()
    
    # Configure the application with the specified environment
    app = configure_app(app, args.env)
    
    # Initialize and seed database if requested
    if args.init_db:
        with app.app_context():
            db.create_all()
            print("Database tables created.")
    
    if args.seed_db:
        with app.app_context():
            seed_db()
    
    # Start the server
    run_server(host=args.host, port=args.port, debug=args.debug)
