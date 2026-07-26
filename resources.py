"""
Astronomy API Resources
=====================
Resource classes for the Astronomy Observations API.

This module defines the Flask-RESTful resources that implement
the API endpoints for all database entities.
"""

from flask import request
from flask_restful import Resource
from datetime import datetime
from models import Type, Property, Place, Instrument, Object, Observation
from database import db
import json


# =========================================================================
# Type Resources
# =========================================================================

class TypeListResource(Resource):
    """Resource for listing and creating types."""
    
    def get(self):
        """Get all types."""
        types = Type.query.all()
        
        result = []
        for type_obj in types:
            result.append({
                'id': type_obj.id,
                'name': type_obj.name
            })
        
        return result
    
    def post(self):
        """Create a new type."""
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        # Validate input
        if 'name' not in json_data:
            return {'message': 'Name is required'}, 400
        
        # Create type
        type_obj = Type(
            name=json_data['name']
        )
        
        if 'id' in json_data:
            type_obj.id = json_data['id']
        
        db.session.add(type_obj)
        db.session.commit()
        
        return {
            'id': type_obj.id,
            'name': type_obj.name
        }, 201


class TypeResource(Resource):
    """Resource for individual type operations."""
    
    def get(self, type_id):
        """Get a specific type."""
        type_obj = Type.query.get(type_id)
        
        if not type_obj:
            return {'message': 'Type not found'}, 404
        
        return {
            'id': type_obj.id,
            'name': type_obj.name
        }
    
    def put(self, type_id):
        """Update a specific type."""
        type_obj = Type.query.get(type_id)
        
        if not type_obj:
            return {'message': 'Type not found'}, 404
        
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        # Update type
        if 'name' in json_data:
            type_obj.name = json_data['name']
        
        db.session.commit()
        
        return {
            'id': type_obj.id,
            'name': type_obj.name
        }
    
    def delete(self, type_id):
        """Delete a specific type."""
        type_obj = Type.query.get(type_id)
        
        if not type_obj:
            return {'message': 'Type not found'}, 404
        
        # Check if the type is in use
        objects = Object.query.filter_by(type=type_id).all()
        if objects:
            return {'message': 'Cannot delete type that is in use'}, 400
        
        db.session.delete(type_obj)
        db.session.commit()
        
        return {'message': 'Type deleted successfully'}, 204


# =========================================================================
# Property Resources
# =========================================================================

class PropertyListResource(Resource):
    """Resource for listing and creating properties."""
    
    def get(self):
        """Get all properties."""
        properties = Property.query.all()
        
        result = []
        for prop in properties:
            result.append({
                'id': prop.id,
                'name': prop.name,
                'valueType': prop.valueType
            })
        
        return result
    
    def post(self):
        """Create a new property."""
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        # Validate input
        if 'name' not in json_data:
            return {'message': 'Name is required'}, 400
        
        if 'valueType' not in json_data:
            return {'message': 'Value type is required'}, 400
        
        # Create property
        prop = Property(
            name=json_data['name'],
            valueType=json_data['valueType']
        )
        
        if 'id' in json_data:
            prop.id = json_data['id']
        
        db.session.add(prop)
        db.session.commit()
        
        return {
            'id': prop.id,
            'name': prop.name,
            'valueType': prop.valueType
        }, 201


class PropertyResource(Resource):
    """Resource for individual property operations."""
    
    def get(self, property_id):
        """Get a specific property."""
        prop = Property.query.get(property_id)
        
        if not prop:
            return {'message': 'Property not found'}, 404
        
        return {
            'id': prop.id,
            'name': prop.name,
            'valueType': prop.valueType
        }
    
    def put(self, property_id):
        """Update a specific property."""
        prop = Property.query.get(property_id)
        
        if not prop:
            return {'message': 'Property not found'}, 404
        
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        # Update property
        if 'name' in json_data:
            prop.name = json_data['name']
        
        if 'valueType' in json_data:
            prop.valueType = json_data['valueType']
        
        db.session.commit()
        
        return {
            'id': prop.id,
            'name': prop.name,
            'valueType': prop.valueType
        }
    
    def delete(self, property_id):
        """Delete a specific property."""
        prop = Property.query.get(property_id)
        
        if not prop:
            return {'message': 'Property not found'}, 404
        
        # Check if the property is in use
        observations = Observation.query.filter_by(prop1=property_id).all()
        if observations:
            return {'message': 'Cannot delete property that is in use'}, 400
        
        db.session.delete(prop)
        db.session.commit()
        
        return {'message': 'Property deleted successfully'}, 204


# =========================================================================
# Place Resources
# =========================================================================

class PlaceListResource(Resource):
    """Resource for listing and creating places."""
    
    def get(self):
        """Get all places."""
        places = Place.query.all()
        
        result = []
        for place in places:
            result.append({
                'id': place.id,
                'name': place.name,
                'alias': place.alias,
                'lat': place.lat,
                'lon': place.lon,
                'alt': place.alt,
                'timezone': place.timezone
            })
        
        return result
    
    def post(self):
        """Create a new place."""
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        # Validate input
        if 'name' not in json_data:
            return {'message': 'Name is required'}, 400
        
        if 'lat' not in json_data:
            return {'message': 'Latitude is required'}, 400
        
        if 'lon' not in json_data:
            return {'message': 'Longitude is required'}, 400
        
        # Create place
        place = Place(
            name=json_data['name'],
            alias=json_data.get('alias'),
            lat=json_data['lat'],
            lon=json_data['lon'],
            alt=json_data.get('alt'),
            timezone=json_data.get('timezone')
        )

        db.session.add(place)
        db.session.commit()

        return {
            'id': place.id,
            'name': place.name,
            'alias': place.alias,
            'lat': place.lat,
            'lon': place.lon,
            'alt': place.alt,
            'timezone': place.timezone
        }, 201


class PlaceResource(Resource):
    """Resource for individual place operations."""
    
    def get(self, place_id):
        """Get a specific place."""
        place = Place.query.get(place_id)
        
        if not place:
            return {'message': 'Place not found'}, 404
        
        return {
            'id': place.id,
            'name': place.name,
            'alias': place.alias,
            'lat': place.lat,
            'lon': place.lon,
            'alt': place.alt,
            'timezone': place.timezone
        }

    def put(self, place_id):
        """Update a specific place."""
        place = Place.query.get(place_id)
        
        if not place:
            return {'message': 'Place not found'}, 404
        
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        # Update place
        if 'name' in json_data:
            place.name = json_data['name']

        if 'alias' in json_data:
            place.alias = json_data['alias']

        if 'lat' in json_data:
            place.lat = json_data['lat']

        if 'lon' in json_data:
            place.lon = json_data['lon']

        if 'alt' in json_data:
            place.alt = json_data['alt']

        if 'timezone' in json_data:
            place.timezone = json_data['timezone']

        db.session.commit()

        return {
            'id': place.id,
            'name': place.name,
            'alias': place.alias,
            'lat': place.lat,
            'lon': place.lon,
            'alt': place.alt,
            'timezone': place.timezone
        }
    
    def delete(self, place_id):
        """Delete a specific place."""
        place = Place.query.get(place_id)
        
        if not place:
            return {'message': 'Place not found'}, 404
        
        # Check if the place is in use
        observations = Observation.query.filter_by(place=place_id).all()
        if observations:
            return {'message': 'Cannot delete place that is in use'}, 400
        
        db.session.delete(place)
        db.session.commit()
        
        return {'message': 'Place deleted successfully'}, 204


# =========================================================================
# Instrument Resources
# =========================================================================

class InstrumentListResource(Resource):
    """Resource for listing and creating instruments."""
    
    def get(self):
        """Get all instruments."""
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
    
    def post(self):
        """Create a new instrument."""
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        # Validate input
        if 'name' not in json_data:
            return {'message': 'Name is required'}, 400
        
        # Create instrument
        instrument = Instrument(
            name=json_data['name'],
            aperture=json_data.get('aperture'),
            power=json_data.get('power')
        )
        
        if 'id' in json_data:
            instrument.id = json_data['id']
        
        db.session.add(instrument)
        db.session.commit()
        
        return {
            'id': instrument.id,
            'name': instrument.name,
            'aperture': instrument.aperture,
            'power': instrument.power
        }, 201


class InstrumentResource(Resource):
    """Resource for individual instrument operations."""
    
    def get(self, instrument_id):
        """Get a specific instrument."""
        instrument = Instrument.query.get(instrument_id)
        
        if not instrument:
            return {'message': 'Instrument not found'}, 404
        
        return {
            'id': instrument.id,
            'name': instrument.name,
            'aperture': instrument.aperture,
            'power': instrument.power
        }
    
    def put(self, instrument_id):
        """Update a specific instrument."""
        instrument = Instrument.query.get(instrument_id)
        
        if not instrument:
            return {'message': 'Instrument not found'}, 404
        
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        # Update instrument
        if 'name' in json_data:
            instrument.name = json_data['name']
        
        if 'aperture' in json_data:
            instrument.aperture = json_data['aperture']
        
        if 'power' in json_data:
            instrument.power = json_data['power']
        
        db.session.commit()
        
        return {
            'id': instrument.id,
            'name': instrument.name,
            'aperture': instrument.aperture,
            'power': instrument.power
        }
    
    def delete(self, instrument_id):
        """Delete a specific instrument."""
        instrument = Instrument.query.get(instrument_id)
        
        if not instrument:
            return {'message': 'Instrument not found'}, 404
        
        # Check if the instrument is in use
        observations = Observation.query.filter_by(instrument=instrument_id).all()
        if observations:
            return {'message': 'Cannot delete instrument that is in use'}, 400
        
        db.session.delete(instrument)
        db.session.commit()
        
        return {'message': 'Instrument deleted successfully'}, 204


# =========================================================================
# Object Resources
# =========================================================================

class ObjectListResource(Resource):
    """Resource for listing and creating objects."""
    
    def get(self):
        """Get all objects."""
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
    
    def post(self):
        """Create a new object."""
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        # Validate input
        if 'name' not in json_data:
            return {'message': 'Name is required'}, 400
        
        if 'type' not in json_data:
            return {'message': 'Type is required'}, 400
        
        # Validate type exists
        type_obj = Type.query.get(json_data['type'])
        if not type_obj:
            return {'message': 'Type not found'}, 400
        
        # Create object
        obj = Object(
            name=json_data['name'],
            desination=json_data.get('desination'),
            type=json_data['type'],
            props=json_data.get('props')
        )
        
        if 'id' in json_data:
            obj.id = json_data['id']
        
        db.session.add(obj)
        db.session.commit()
        
        return {
            'id': obj.id,
            'name': obj.name,
            'desination': obj.desination,
            'type': obj.type,
            'props': obj.props
        }, 201


class ObjectResource(Resource):
    """Resource for individual object operations."""
    
    def get(self, object_id):
        """Get a specific object."""
        obj = Object.query.get(object_id)
        
        if not obj:
            return {'message': 'Object not found'}, 404
        
        return {
            'id': obj.id,
            'name': obj.name,
            'desination': obj.desination,
            'type': obj.type,
            'props': obj.props
        }
    
    def put(self, object_id):
        """Update a specific object."""
        obj = Object.query.get(object_id)
        
        if not obj:
            return {'message': 'Object not found'}, 404
        
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        # Validate type exists if provided
        if 'type' in json_data:
            type_obj = Type.query.get(json_data['type'])
            if not type_obj:
                return {'message': 'Type not found'}, 400
            obj.type = json_data['type']
        
        # Update object
        if 'name' in json_data:
            obj.name = json_data['name']
        
        if 'desination' in json_data:
            obj.desination = json_data['desination']
        
        if 'props' in json_data:
            obj.props = json_data['props']
        
        db.session.commit()
        
        return {
            'id': obj.id,
            'name': obj.name,
            'desination': obj.desination,
            'type': obj.type,
            'props': obj.props
        }
    
    def delete(self, object_id):
        """Delete a specific object."""
        obj = Object.query.get(object_id)
        
        if not obj:
            return {'message': 'Object not found'}, 404
        
        # Check if the object is in use
        observations = Observation.query.filter_by(object=object_id).all()
        if observations:
            return {'message': 'Cannot delete object that is in use'}, 400
        
        db.session.delete(obj)
        db.session.commit()
        
        return {'message': 'Object deleted successfully'}, 204


# =========================================================================
# Observation Resources
# =========================================================================

class ObservationListResource(Resource):
    """Resource for listing and creating observations."""
    
    def get(self):
        """Get all observations."""
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
    
    def post(self):
        """Create a new observation."""
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        # Validate input
        if 'object' not in json_data:
            return {'message': 'Object is required'}, 400
        
        if 'place' not in json_data:
            return {'message': 'Place is required'}, 400
        
        if 'instrument' not in json_data:
            return {'message': 'Instrument is required'}, 400
        
        if 'datetime' not in json_data:
            return {'message': 'Datetime is required'}, 400
        
        if 'observation' not in json_data:
            return {'message': 'Observation text is required'}, 400
        
        # Validate foreign keys
        obj = Object.query.get(json_data['object'])
        if not obj:
            return {'message': 'Object not found'}, 400
        
        place = Place.query.get(json_data['place'])
        if not place:
            return {'message': 'Place not found'}, 400
        
        instrument = Instrument.query.get(json_data['instrument'])
        if not instrument:
            return {'message': 'Instrument not found'}, 400
        
        # Validate property if provided
        if 'prop1' in json_data and json_data['prop1']:
            prop = Property.query.get(json_data['prop1'])
            if not prop:
                return {'message': 'Property not found'}, 400
        
        # Parse datetime
        try:
            observation_datetime = datetime.fromisoformat(json_data['datetime'].replace('Z', '+00:00'))
        except Exception:
            return {'message': 'Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}, 400
        
        # Create observation
        observation = Observation(
            object=json_data['object'],
            place=json_data['place'],
            instrument=json_data['instrument'],
            datetime=observation_datetime,
            observation=json_data['observation'],
            prop1=json_data.get('prop1'),
            prop1value=json_data.get('prop1value')
        )
        
        db.session.add(observation)
        db.session.commit()
        
        return {
            'id': observation.id,
            'object': observation.object,
            'place': observation.place,
            'instrument': observation.instrument,
            'datetime': observation.datetime.isoformat() if observation.datetime else None,
            'observation': observation.observation,
            'prop1': observation.prop1,
            'prop1value': observation.prop1value
        }, 201


class ObservationResource(Resource):
    """Resource for individual observation operations."""
    
    def get(self, observation_id):
        """Get a specific observation."""
        observation = Observation.query.get(observation_id)
        
        if not observation:
            return {'message': 'Observation not found'}, 404
        
        return {
            'id': observation.id,
            'object': observation.object,
            'place': observation.place,
            'instrument': observation.instrument,
            'datetime': observation.datetime.isoformat() if observation.datetime else None,
            'observation': observation.observation,
            'prop1': observation.prop1,
            'prop1value': observation.prop1value
        }
    
    def put(self, observation_id):
        """Update a specific observation."""
        observation = Observation.query.get(observation_id)
        
        if not observation:
            return {'message': 'Observation not found'}, 404
        
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        # Validate foreign keys if provided
        if 'object' in json_data:
            obj = Object.query.get(json_data['object'])
            if not obj:
                return {'message': 'Object not found'}, 400
            observation.object = json_data['object']
        
        if 'place' in json_data:
            place = Place.query.get(json_data['place'])
            if not place:
                return {'message': 'Place not found'}, 400
            observation.place = json_data['place']
        
        if 'instrument' in json_data:
            instrument = Instrument.query.get(json_data['instrument'])
            if not instrument:
                return {'message': 'Instrument not found'}, 400
            observation.instrument = json_data['instrument']
        
        if 'prop1' in json_data and json_data['prop1']:
            prop = Property.query.get(json_data['prop1'])
            if not prop:
                return {'message': 'Property not found'}, 400
            observation.prop1 = json_data['prop1']
        
        # Parse datetime if provided
        if 'datetime' in json_data:
            try:
                observation_datetime = datetime.fromisoformat(json_data['datetime'].replace('Z', '+00:00'))
                observation.datetime = observation_datetime
            except Exception:
                return {'message': 'Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}, 400
        
        # Update observation
        if 'observation' in json_data:
            observation.observation = json_data['observation']
        
        if 'prop1value' in json_data:
            observation.prop1value = json_data['prop1value']
        
        db.session.commit()
        
        return {
            'id': observation.id,
            'object': observation.object,
            'place': observation.place,
            'instrument': observation.instrument,
            'datetime': observation.datetime.isoformat() if observation.datetime else None,
            'observation': observation.observation,
            'prop1': observation.prop1,
            'prop1value': observation.prop1value
        }
    
    def delete(self, observation_id):
        """Delete a specific observation."""
        observation = Observation.query.get(observation_id)
        
        if not observation:
            return {'message': 'Observation not found'}, 404
        
        db.session.delete(observation)
        db.session.commit()
        
        return {'message': 'Observation deleted successfully'}, 204


# =========================================================================
# Relationship Resources
# =========================================================================

class ObjectObservationsResource(Resource):
    """Resource for retrieving observations of a specific object."""
    
    def get(self, object_id):
        """Get all observations for a specific object."""
        # Check if object exists
        obj = Object.query.get(object_id)
        if not obj:
            return {'message': 'Object not found'}, 404
        
        # Get observations
        observations = Observation.query.filter_by(object=object_id).all()
        
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


class PlaceObservationsResource(Resource):
    """Resource for retrieving observations at a specific place."""
    
    def get(self, place_id):
        """Get all observations for a specific place."""
        # Check if place exists
        place = Place.query.get(place_id)
        if not place:
            return {'message': 'Place not found'}, 404
        
        # Get observations
        observations = Observation.query.filter_by(place=place_id).all()
        
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


class InstrumentObservationsResource(Resource):
    """Resource for retrieving observations made with a specific instrument."""
    
    def get(self, instrument_id):
        """Get all observations for a specific instrument."""
        # Check if instrument exists
        instrument = Instrument.query.get(instrument_id)
        if not instrument:
            return {'message': 'Instrument not found'}, 404
        
        # Get observations
        observations = Observation.query.filter_by(instrument=instrument_id).all()
        
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


# =========================================================================
# Search Resources
# =========================================================================

class ObservationSearchResource(Resource):
    """Resource for searching observations with filters."""
    
    def get(self):
        """Search observations with filters."""
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        object_id = request.args.get('object_id')
        place_id = request.args.get('place_id')
        instrument_id = request.args.get('instrument_id')
        
        # Build query
        query = Observation.query
        
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(Observation.datetime >= start_datetime)
            except Exception:
                return {'message': 'Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}, 400
        
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(Observation.datetime <= end_datetime)
            except Exception:
                return {'message': 'Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}, 400
        
        if object_id:
            try:
                object_id = int(object_id)
                query = query.filter(Observation.object == object_id)
            except ValueError:
                return {'message': 'Invalid object_id format. Must be an integer'}, 400
        
        if place_id:
            try:
                place_id = int(place_id)
                query = query.filter(Observation.place == place_id)
            except ValueError:
                return {'message': 'Invalid place_id format. Must be an integer'}, 400
        
        if instrument_id:
            try:
                instrument_id = int(instrument_id)
                query = query.filter(Observation.instrument == instrument_id)
            except ValueError:
                return {'message': 'Invalid instrument_id format. Must be an integer'}, 400
        
        # Execute query
        observations = query.all()

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


# =========================================================================
# External Data Integrations (SIMBAD search & AAVSO VSP finder charts)
# =========================================================================

# Standard AAVSO VSP chart scales (field of view in degrees), mirroring the
# web interface's finder-chart scales so API clients can request by key.
VSP_CHART_SCALES = [
    {'key': 'A',  'fov': 180, 'label': 'A (3 deg)'},
    {'key': 'AB', 'fov': 120, 'label': 'AB (2 deg)'},
    {'key': 'B',  'fov': 60,  'label': 'B (1 deg)'},
    {'key': 'C',  'fov': 20,  'label': 'C (20 arcmin)'},
    {'key': 'D',  'fov': 10,  'label': 'D (10 arcmin)'},
    {'key': 'E',  'fov': 5,   'label': 'E (5 arcmin)'},
    {'key': 'F',  'fov': 2,   'label': 'F (2 arcmin)'},
]


class SimbadSearchResource(Resource):
    """Search the SIMBAD astronomical database.

    Query params:
        q             search term (required)
        type          one of name | wildcard | type_variable |
                      variable_constellation (default: name)
        max           max records, 1..2000 (default: 50)
        var_type      variable-star type (for variable_constellation)
        constellation constellation name/abbr (for variable_constellation)
    """

    def get(self):
        query = (request.args.get('q') or '').strip()
        if not query:
            return {'message': 'Missing required query parameter: q'}, 400

        search_type = (request.args.get('type') or 'name').strip()
        allowed = ('name', 'wildcard', 'type_variable', 'variable_constellation')
        if search_type not in allowed:
            return {'message': 'Invalid type. Allowed: ' + ', '.join(allowed)}, 400

        max_records = request.args.get('max', '50')
        var_type = request.args.get('var_type')
        constellation = request.args.get('constellation')

        try:
            from import_simbad import search_simbad
            results = search_simbad(
                query, search_type=search_type, max_records=max_records,
                var_type=var_type, constellation=constellation
            )
        except Exception as e:
            return {'message': 'SIMBAD query failed: ' + str(e)}, 502

        results = results or []
        return {
            'query': query,
            'type': search_type,
            'count': len(results),
            'results': results,
        }


class VspChartResource(Resource):
    """Look up an AAVSO VSP finder chart for a star (metadata + image URL).

    Query params:
        star      star name/designation (required)
        scale     chart scale key A, AB, B, C, D, E, F (maps to a field of view)
        fov       explicit field of view in degrees (overrides scale)
        maglimit  faintest magnitude to plot (default: 14.5)

    Returns the AAVSO chart id, the chart image URL and the comparison-star
    photometry. Does not download or store the image (see the web interface
    for local caching); this endpoint just resolves the chart.
    """

    def get(self):
        star = (request.args.get('star') or '').strip()
        if not star:
            return {'message': 'Missing required query parameter: star'}, 400

        scale = (request.args.get('scale') or '').strip().upper()
        fov = request.args.get('fov')
        if fov:
            try:
                fov = float(fov)
            except ValueError:
                return {'message': 'Invalid fov (expected degrees)'}, 400
        elif scale:
            match = next((s for s in VSP_CHART_SCALES if s['key'] == scale), None)
            if not match:
                keys = ', '.join(s['key'] for s in VSP_CHART_SCALES)
                return {'message': 'Invalid scale. Allowed: ' + keys}, 400
            fov = match['fov']
        else:
            fov = 60  # default ~1 degree (scale B)

        try:
            maglimit = float(request.args.get('maglimit', '14.5'))
        except ValueError:
            maglimit = 14.5

        try:
            import requests as _requests
            resp = _requests.get(
                'https://app.aavso.org/vsp/api/chart/',
                params={'format': 'json', 'star': star, 'fov': fov, 'maglimit': maglimit},
                timeout=15,
            )
        except Exception as e:
            return {'message': 'VSP request failed: ' + str(e)}, 502

        if resp.status_code != 200:
            return {'message': 'VSP API error: HTTP ' + str(resp.status_code)}, 502

        try:
            data = resp.json()
        except ValueError:
            return {'message': 'VSP returned a non-JSON response'}, 502

        image_uri = (data.get('image_uri') or '').replace('?format=json', '')
        return {
            'star': data.get('star', star),
            'chartid': data.get('chartid', ''),
            'fov': fov,
            'maglimit': maglimit,
            'image_uri': image_uri,
            'comparison_stars': data.get('photometry', []),
        }


class VspChartScalesResource(Resource):
    """List the available AAVSO VSP finder-chart scales."""

    def get(self):
        return {'scales': VSP_CHART_SCALES}
