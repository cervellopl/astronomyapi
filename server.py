# =============================================================================
# Root Endpoint - API Documentation
# =============================================================================

"""
Astronomy API Server
==================
Main entry point for the Astronomy Observations API server.

This script:
- Sets up the Flask application
- Registers API resources
- Initializes the database
- Runs the server
"""

import os
from flask import Flask, jsonify, redirect, url_for
from flask_restful import Api

# Import configuration and database
from config import app
from database import db

# Import models to ensure they're registered with SQLAlchemy
from models import *

# Import resources after models to avoid circular imports
from resources import (
    TypeListResource, TypeResource,
    PropertyListResource, PropertyResource,
    PlaceListResource, PlaceResource,
    InstrumentListResource, InstrumentResource,
    ObjectListResource, ObjectResource,
    ObservationListResource, ObservationResource,
    ObjectObservationsResource, PlaceObservationsResource,
    InstrumentObservationsResource, ObservationSearchResource
)

# Import web interface
from web_routes import web

# Initialize API
api = Api(app)

# Register web blueprint
app.register_blueprint(web, url_prefix='/web')


# =============================================================================
# Register API Resources
# =============================================================================

# Type resources
api.add_resource(TypeListResource, '/api/types')
api.add_resource(TypeResource, '/api/types/<int:type_id>')

# Property resources
api.add_resource(PropertyListResource, '/api/properties')
api.add_resource(PropertyResource, '/api/properties/<int:property_id>')

# Place resources
api.add_resource(PlaceListResource, '/api/places')
api.add_resource(PlaceResource, '/api/places/<int:place_id>')

# Instrument resources
api.add_resource(InstrumentListResource, '/api/instruments')
api.add_resource(InstrumentResource, '/api/instruments/<int:instrument_id>')

# Object resources
api.add_resource(ObjectListResource, '/api/objects')
api.add_resource(ObjectResource, '/api/objects/<int:object_id>')

# Observation resources
api.add_resource(ObservationListResource, '/api/observations')
api.add_resource(ObservationResource, '/api/observations/<int:observation_id>')

# Relationship resources
api.add_resource(ObjectObservationsResource, '/api/objects/<int:object_id>/observations')
api.add_resource(PlaceObservationsResource, '/api/places/<int:place_id>/observations')
api.add_resource(InstrumentObservationsResource, '/api/instruments/<int:instrument_id>/observations')

# Search resources
api.add_resource(ObservationSearchResource, '/api/observations/search')


# =============================================================================
# Root Endpoint - API Documentation
# =============================================================================

@app.route('/')
def index():
    """API documentation endpoint."""
    return jsonify({
        'api': 'Astronomy Observations API',
        'version': '1.0.0',
        'description': 'RESTful API for managing astronomical observations',
        'web_interface': '/web',
        'endpoints': {
            'types': {
                'GET /api/types': 'Get all types',
                'POST /api/types': 'Create a new type',
                'GET /api/types/<id>': 'Get a specific type',
                'PUT /api/types/<id>': 'Update a specific type',
                'DELETE /api/types/<id>': 'Delete a specific type'
            },
            'properties': {
                'GET /api/properties': 'Get all properties',
                'POST /api/properties': 'Create a new property',
                'GET /api/properties/<id>': 'Get a specific property',
                'PUT /api/properties/<id>': 'Update a specific property',
                'DELETE /api/properties/<id>': 'Delete a specific property'
            },
            'places': {
                'GET /api/places': 'Get all places',
                'POST /api/places': 'Create a new place',
                'GET /api/places/<id>': 'Get a specific place',
                'PUT /api/places/<id>': 'Update a specific place',
                'DELETE /api/places/<id>': 'Delete a specific place',
                'GET /api/places/<id>/observations': 'Get all observations made at a specific place'
            },
            'instruments': {
                'GET /api/instruments': 'Get all instruments',
                'POST /api/instruments': 'Create a new instrument',
                'GET /api/instruments/<id>': 'Get a specific instrument',
                'PUT /api/instruments/<id>': 'Update a specific instrument',
                'DELETE /api/instruments/<id>': 'Delete a specific instrument',
                'GET /api/instruments/<id>/observations': 'Get all observations made with a specific instrument'
            },
            'objects': {
                'GET /api/objects': 'Get all objects',
                'POST /api/objects': 'Create a new object',
                'GET /api/objects/<id>': 'Get a specific object',
                'PUT /api/objects/<id>': 'Update a specific object',
                'DELETE /api/objects/<id>': 'Delete a specific object',
                'GET /api/objects/<id>/observations': 'Get all observations of a specific object'
            },
            'observations': {
                'GET /api/observations': 'Get all observations',
                'POST /api/observations': 'Create a new observation',
                'GET /api/observations/<id>': 'Get a specific observation',
                'PUT /api/observations/<id>': 'Update a specific observation',
                'DELETE /api/observations/<id>': 'Delete a specific observation',
                'GET /api/observations/search': 'Search observations with filters (params: start_date, end_date, object_id, place_id, instrument_id)'
            }
        }
    })


# =============================================================================
# Web Interface Redirect
# =============================================================================

@app.route('/web')
def web_redirect():
    """Redirect to web interface dashboard."""
    return redirect(url_for('web.dashboard'))


# =============================================================================
# Error Handlers
# =============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found'
    }), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == '__main__':
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Run the Astronomy Observations API server')
    parser.add_argument('--host', '-H', default='0.0.0.0', help='Host address to bind to')
    parser.add_argument('--port', '-p', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--env', '-e', choices=['development', 'testing', 'production'], 
                        default='development', help='Environment configuration to use')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Start the server
    app.run(host=args.host, port=args.port, debug=args.debug)
