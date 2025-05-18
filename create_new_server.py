"""
Create a completely new server.py file
"""

def create_new_server():
    """Create a completely new server.py file"""
    print("Creating a completely new server.py file...")
    
    # Content for the new server.py
    content = '''"""
Astronomy API Server - Fresh Installation
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
db_instance = configure_db(app)

# Initialize API
api = Api(app)

# Import resources after models to avoid circular imports
try:
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

    # Register API Resources
    api.add_resource(TypeListResource, '/api/types')
    api.add_resource(TypeResource, '/api/types/<int:type_id>')
    api.add_resource(PropertyListResource, '/api/properties')
    api.add_resource(PropertyResource, '/api/properties/<int:property_id>')
    api.add_resource(PlaceListResource, '/api/places')
    api.add_resource(PlaceResource, '/api/places/<int:place_id>')
    api.add_resource(InstrumentListResource, '/api/instruments')
    api.add_resource(InstrumentResource, '/api/instruments/<int:instrument_id>')
    api.add_resource(ObjectListResource, '/api/objects')
    api.add_resource(ObjectResource, '/api/objects/<int:object_id>')
    api.add_resource(ObservationListResource, '/api/observations')
    api.add_resource(ObservationResource, '/api/observations/<int:observation_id>')
    api.add_resource(ObjectObservationsResource, '/api/objects/<int:object_id>/observations')
    api.add_resource(PlaceObservationsResource, '/api/places/<int:place_id>/observations')
    api.add_resource(InstrumentObservationsResource, '/api/instruments/<int:instrument_id>/observations')
    api.add_resource(ObservationSearchResource, '/api/observations/search')
    
    print("API resources registered successfully")
except Exception as e:
    print(f"Error registering API resources: {str(e)}")

# Import web interface
try:
    from web_routes import web
    
    # Register web blueprint
    app.register_blueprint(web, url_prefix='/web')
    print("Web interface registered successfully")
except Exception as e:
    print(f"Error registering web interface: {str(e)}")
    # Continue without web interface

# Root endpoint
@app.route('/')
def index():
    """Root endpoint - API documentation."""
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
                'GET /api/observations/search': 'Search observations with filters'
            }
        }
    })

# Web interface redirect
@app.route('/web')
def web_redirect():
    """Redirect to web interface dashboard."""
    return redirect(url_for('web.dashboard'))

# Health check endpoint
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

# Error handlers
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

# Main entry point
if __name__ == '__main__':
    # Start the server
    app.run(host='0.0.0.0', port=5000, debug=True)
'''
    
    # Write the new server.py file
    try:
        with open('server.py', 'w') as f:
            f.write(content)
        print("Created new server.py file")
        return True
    except Exception as e:
        print(f"Error creating server.py: {str(e)}")
        return False

if __name__ == '__main__':
    create_new_server()
