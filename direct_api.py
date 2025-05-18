"""
Direct API implementation for web interface
==================================
This file provides direct access to database models without using HTTP requests.

This approach avoids URL scheme issues by directly accessing the database.
"""

from flask import current_app
from models import Type, Property, Place, Instrument, Object, Observation
from database import db

# Function to get all types
def get_types():
    """Get all types directly from the database."""
    try:
        with current_app.app_context():
            types = Type.query.all()
            result = []
            for type_obj in types:
                result.append({
                    'id': type_obj.id,
                    'name': type_obj.name
                })
            return result
    except Exception as e:
        print(f"Error getting types: {str(e)}")
        return []

# Function to get all properties
def get_properties():
    """Get all properties directly from the database."""
    try:
        with current_app.app_context():
            properties = Property.query.all()
            result = []
            for prop in properties:
                result.append({
                    'id': prop.id,
                    'name': prop.name,
                    'valueType': prop.valueType
                })
            return result
    except Exception as e:
        print(f"Error getting properties: {str(e)}")
        return []

# Function to get all places
def get_places():
    """Get all places directly from the database."""
    try:
        with current_app.app_context():
            places = Place.query.all()
            result = []
            for place in places:
                result.append({
                    'id': place.id,
                    'name': place.name,
                    'lat': place.lat,
                    'lon': place.lon,
                    'alt': place.alt,
                    'timezone': place.timezone
                })
            return result
    except Exception as e:
        print(f"Error getting places: {str(e)}")
        return []

# Function to get all instruments
def get_instruments():
    """Get all instruments directly from the database."""
    try:
        with current_app.app_context():
            instruments = Instrument.query.all()
            result = []
            for instrument in instruments:
                result.append({
                    'id': instrument.id,
                    'name': instrument.name,
                    'aperture': instrument.aperture,
                    'power': instrument.power
                })
            return result
    except Exception as e:
        print(f"Error getting instruments: {str(e)}")
        return []

# Function to get all objects
def get_objects():
    """Get all objects directly from the database."""
    try:
        with current_app.app_context():
            objects = Object.query.all()
            result = []
            for obj in objects:
                result.append({
                    'id': obj.id,
                    'name': obj.name,
                    'desination': obj.desination,
                    'type': obj.type,
                    'props': obj.props
                })
            return result
    except Exception as e:
        print(f"Error getting objects: {str(e)}")
        return []

# Function to get all observations
def get_observations():
    """Get all observations directly from the database."""
    try:
        with current_app.app_context():
            observations = Observation.query.all()
            result = []
            for obs in observations:
                result.append({
                    'id': obs.id,
                    'object': obs.object,
                    'place': obs.place,
                    'instrument': obs.instrument,
                    'datetime': obs.datetime.isoformat() if obs.datetime else None,
                    'observation': obs.observation,
                    'prop1': obs.prop1,
                    'prop1value': obs.prop1value
                })
            return result
    except Exception as e:
        print(f"Error getting observations: {str(e)}")
        return []

# Function to get a specific type
def get_type(type_id):
    """Get a specific type by ID."""
    try:
        with current_app.app_context():
            type_obj = Type.query.get(type_id)
            if type_obj:
                return {
                    'id': type_obj.id,
                    'name': type_obj.name
                }
            return None
    except Exception as e:
        print(f"Error getting type {type_id}: {str(e)}")
        return None

# Function to get a specific property
def get_property(property_id):
    """Get a specific property by ID."""
    try:
        with current_app.app_context():
            prop = Property.query.get(property_id)
            if prop:
                return {
                    'id': prop.id,
                    'name': prop.name,
                    'valueType': prop.valueType
                }
            return None
    except Exception as e:
        print(f"Error getting property {property_id}: {str(e)}")
        return None

# Function to get a specific place
def get_place(place_id):
    """Get a specific place by ID."""
    try:
        with current_app.app_context():
            place = Place.query.get(place_id)
            if place:
                return {
                    'id': place.id,
                    'name': place.name,
                    'lat': place.lat,
                    'lon': place.lon,
                    'alt': place.alt,
                    'timezone': place.timezone
                }
            return None
    except Exception as e:
        print(f"Error getting place {place_id}: {str(e)}")
        return None

# Function to get a specific instrument
def get_instrument(instrument_id):
    """Get a specific instrument by ID."""
    try:
        with current_app.app_context():
            instrument = Instrument.query.get(instrument_id)
            if instrument:
                return {
                    'id': instrument.id,
                    'name': instrument.name,
                    'aperture': instrument.aperture,
                    'power': instrument.power
                }
            return None
    except Exception as e:
        print(f"Error getting instrument {instrument_id}: {str(e)}")
        return None

# Function to get a specific object
def get_object(object_id):
    """Get a specific object by ID."""
    try:
        with current_app.app_context():
            obj = Object.query.get(object_id)
            if obj:
                return {
                    'id': obj.id,
                    'name': obj.name,
                    'desination': obj.desination,
                    'type': obj.type,
                    'props': obj.props
                }
            return None
    except Exception as e:
        print(f"Error getting object {object_id}: {str(e)}")
        return None

# Function to get a specific observation
def get_observation(observation_id):
    """Get a specific observation by ID."""
    try:
        with current_app.app_context():
            obs = Observation.query.get(observation_id)
            if obs:
                return {
                    'id': obs.id,
                    'object': obs.object,
                    'place': obs.place,
                    'instrument': obs.instrument,
                    'datetime': obs.datetime.isoformat() if obs.datetime else None,
                    'observation': obs.observation,
                    'prop1': obs.prop1,
                    'prop1value': obs.prop1value
                }
            return None
    except Exception as e:
        print(f"Error getting observation {observation_id}: {str(e)}")
        return None

# Class to mimic requests.Response
class MockResponse:
    """Mock response object to mimic requests.Response."""
    
    def __init__(self, data, status_code=200):
        self.data = data
        self.status_code = status_code
    
    def json(self):
        """Return data as JSON."""
        return self.data

# Function to mimic api_request
def api_request(method, endpoint, data=None, params=None):
    """
    Mock API request function that directly accesses the database.
    
    Args:
        method (str): HTTP method (GET, POST, PUT, DELETE)
        endpoint (str): API endpoint
        data (dict, optional): Data for POST/PUT requests
        params (dict, optional): Query parameters
        
    Returns:
        MockResponse object
    """
    print(f"Direct API access: {method} {endpoint}")
    
    # GET endpoints
    if method == 'GET':
        # Types endpoints
        if endpoint == '/api/types':
            return MockResponse(get_types())
        elif endpoint.startswith('/api/types/'):
            type_id = int(endpoint.split('/')[-1])
            return MockResponse(get_type(type_id))
        
        # Properties endpoints
        elif endpoint == '/api/properties':
            return MockResponse(get_properties())
        elif endpoint.startswith('/api/properties/'):
            property_id = int(endpoint.split('/')[-1])
            return MockResponse(get_property(property_id))
        
        # Places endpoints
        elif endpoint == '/api/places':
            return MockResponse(get_places())
        elif endpoint.startswith('/api/places/'):
            place_id = int(endpoint.split('/')[-1])
            return MockResponse(get_place(place_id))
        
        # Instruments endpoints
        elif endpoint == '/api/instruments':
            return MockResponse(get_instruments())
        elif endpoint.startswith('/api/instruments/'):
            instrument_id = int(endpoint.split('/')[-1])
            return MockResponse(get_instrument(instrument_id))
        
        # Objects endpoints
        elif endpoint == '/api/objects':
            return MockResponse(get_objects())
        elif endpoint.startswith('/api/objects/'):
            object_id = int(endpoint.split('/')[-1])
            return MockResponse(get_object(object_id))
        
        # Observations endpoints
        elif endpoint == '/api/observations':
            return MockResponse(get_observations())
        elif endpoint.startswith('/api/observations/'):
            observation_id = int(endpoint.split('/')[-1])
            return MockResponse(get_observation(observation_id))
    
    # Default: Return empty response
    return MockResponse([], 404)
