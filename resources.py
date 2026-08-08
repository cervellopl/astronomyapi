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
from models import (Type, Property, Place, Instrument, Object, Observation,
                    Session, Plan, ObservationProperty)
from database import db
import json


# =========================================================================
# Observation serialization helpers (shared)
# =========================================================================

def _observation_to_dict(obs):
    """Serialize an observation, including its list of properties.

    Keeps the legacy prop1/prop1value fields for backward compatibility;
    the authoritative property list is under 'properties'.
    """
    return {
        'id': obs.id,
        'object': obs.object,
        'place': obs.place,
        'instrument': obs.instrument,
        'session_id': obs.session_id,
        'datetime': obs.datetime.isoformat() if obs.datetime else None,
        'observation': obs.observation,
        'prop1': obs.prop1,
        'prop1value': obs.prop1value,
        'properties': [
            {'id': p.id, 'property': p.property_id, 'value': p.value}
            for p in obs.properties
        ],
    }


def _sync_legacy_prop(obs):
    """Mirror the first property into the legacy prop1/prop1value columns so
    older clients and views keep working."""
    if obs.properties:
        obs.prop1 = obs.properties[0].property_id
        obs.prop1value = obs.properties[0].value
    else:
        obs.prop1 = None
        obs.prop1value = None


def _apply_observation_properties(obs, properties):
    """Replace an observation's properties from a list of {property, value}
    dicts. Returns an error message string, or None on success."""
    if not isinstance(properties, list):
        return 'properties must be a list of {property, value} objects'
    new_rows = []
    for item in properties:
        if not isinstance(item, dict) or 'property' not in item:
            return 'each property entry needs a "property" id (and optional "value")'
        pid = item['property']
        if not Property.query.get(pid):
            return 'Property {} not found'.format(pid)
        new_rows.append(ObservationProperty(property_id=pid, value=item.get('value')))
    obs.properties = new_rows
    return None


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
            result.append(_observation_to_dict(obs))

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
            session_id=json_data.get('session_id'),
            datetime=observation_datetime,
            observation=json_data['observation'],
        )

        # Properties: prefer the multi-property list; fall back to legacy prop1
        if json_data.get('properties') is not None:
            err = _apply_observation_properties(observation, json_data['properties'])
            if err:
                return {'message': err}, 400
        elif json_data.get('prop1') and json_data.get('prop1value'):
            observation.properties = [ObservationProperty(
                property_id=json_data['prop1'], value=json_data.get('prop1value'))]
        _sync_legacy_prop(observation)

        db.session.add(observation)
        db.session.commit()

        return _observation_to_dict(observation), 201


class ObservationResource(Resource):
    """Resource for individual observation operations."""
    
    def get(self, observation_id):
        """Get a specific observation."""
        observation = Observation.query.get(observation_id)
        
        if not observation:
            return {'message': 'Observation not found'}, 404
        
        return _observation_to_dict(observation)
    
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
        
        if 'session_id' in json_data:
            observation.session_id = json_data['session_id']

        # Parse datetime if provided
        if 'datetime' in json_data:
            try:
                observation_datetime = datetime.fromisoformat(json_data['datetime'].replace('Z', '+00:00'))
                observation.datetime = observation_datetime
            except Exception:
                return {'message': 'Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}, 400

        # Update observation text
        if 'observation' in json_data:
            observation.observation = json_data['observation']

        # Properties: `properties` list replaces the whole set; legacy
        # prop1/prop1value updates the first property for back-compat.
        if 'properties' in json_data:
            err = _apply_observation_properties(observation, json_data['properties'])
            if err:
                return {'message': err}, 400
        elif 'prop1' in json_data or 'prop1value' in json_data:
            pid = json_data.get('prop1')
            if pid:
                if not Property.query.get(pid):
                    return {'message': 'Property not found'}, 400
                observation.properties = [ObservationProperty(
                    property_id=pid, value=json_data.get('prop1value'))]
            else:
                observation.properties = []

        _sync_legacy_prop(observation)
        db.session.commit()

        return _observation_to_dict(observation)
    
    def delete(self, observation_id):
        """Delete a specific observation."""
        observation = Observation.query.get(observation_id)
        
        if not observation:
            return {'message': 'Observation not found'}, 404
        
        db.session.delete(observation)
        db.session.commit()
        
        return {'message': 'Observation deleted successfully'}, 204


# =========================================================================
# Session Resources
# =========================================================================

def _parse_dt(value):
    """Parse an ISO datetime string, returning (datetime, error_message)."""
    if value in (None, ''):
        return None, None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')), None
    except Exception:
        return None, 'Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'


def _session_to_dict(s):
    return {
        'id': s.id,
        'number': s.number,
        'start_datetime': s.start_datetime.isoformat() if s.start_datetime else None,
        'end_datetime': s.end_datetime.isoformat() if s.end_datetime else None,
        'cloud_percentage': s.cloud_percentage,
        'cloud_type': s.cloud_type,
        'light_pollution': s.light_pollution,
        'limiting_magnitude': s.limiting_magnitude,
        'moon_phase': s.moon_phase,
        'moon_altitude': s.moon_altitude,
        'instrument': s.instrument,
    }


class SessionListResource(Resource):
    """Resource for listing and creating observation sessions."""

    def get(self):
        """Get all sessions."""
        return [_session_to_dict(s) for s in Session.query.all()]

    def post(self):
        """Create a new session."""
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400

        # Validate instrument foreign key if provided
        if json_data.get('instrument'):
            if not Instrument.query.get(json_data['instrument']):
                return {'message': 'Instrument not found'}, 400

        start_dt, err = _parse_dt(json_data.get('start_datetime'))
        if err:
            return {'message': 'start_datetime: ' + err}, 400
        end_dt, err = _parse_dt(json_data.get('end_datetime'))
        if err:
            return {'message': 'end_datetime: ' + err}, 400

        session = Session(
            number=json_data.get('number'),
            start_datetime=start_dt,
            end_datetime=end_dt,
            cloud_percentage=json_data.get('cloud_percentage'),
            cloud_type=json_data.get('cloud_type'),
            light_pollution=json_data.get('light_pollution'),
            limiting_magnitude=json_data.get('limiting_magnitude'),
            moon_phase=json_data.get('moon_phase'),
            moon_altitude=json_data.get('moon_altitude'),
            instrument=json_data.get('instrument'),
        )
        db.session.add(session)
        db.session.commit()
        return _session_to_dict(session), 201


class SessionResource(Resource):
    """Resource for individual session operations."""

    def get(self, session_id):
        """Get a specific session."""
        session = Session.query.get(session_id)
        if not session:
            return {'message': 'Session not found'}, 404
        return _session_to_dict(session)

    def put(self, session_id):
        """Update a specific session."""
        session = Session.query.get(session_id)
        if not session:
            return {'message': 'Session not found'}, 404

        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400

        if 'instrument' in json_data:
            if json_data['instrument'] and not Instrument.query.get(json_data['instrument']):
                return {'message': 'Instrument not found'}, 400
            session.instrument = json_data['instrument']

        if 'start_datetime' in json_data:
            dt, err = _parse_dt(json_data['start_datetime'])
            if err:
                return {'message': 'start_datetime: ' + err}, 400
            session.start_datetime = dt
        if 'end_datetime' in json_data:
            dt, err = _parse_dt(json_data['end_datetime'])
            if err:
                return {'message': 'end_datetime: ' + err}, 400
            session.end_datetime = dt

        for field in ('number', 'cloud_percentage', 'cloud_type', 'light_pollution',
                      'limiting_magnitude', 'moon_phase', 'moon_altitude'):
            if field in json_data:
                setattr(session, field, json_data[field])

        db.session.commit()
        return _session_to_dict(session)

    def delete(self, session_id):
        """Delete a specific session."""
        session = Session.query.get(session_id)
        if not session:
            return {'message': 'Session not found'}, 404
        db.session.delete(session)
        db.session.commit()
        return {'message': 'Session deleted successfully'}, 204


# =========================================================================
# Plan Resources
# =========================================================================

def _plan_to_dict(p):
    return {
        'id': p.id,
        'name': p.name,
        'star_ids': p.star_ids,
        'stars': [int(s) for s in p.star_id_list() if s.isdigit()],
        'place_id': p.place_id,
        'instrument_id': p.instrument_id,
        'session_id': p.session_id,
        'created_at': p.created_at.isoformat() if p.created_at else None,
    }


def _normalise_star_ids(json_data):
    """Build the comma-separated star_ids string from `stars` (list) or
    `star_ids` (string), or return (None, None) if neither is provided."""
    if 'stars' in json_data and json_data['stars'] is not None:
        return ','.join(str(int(s)) for s in json_data['stars']), None
    if 'star_ids' in json_data and json_data['star_ids'] is not None:
        return str(json_data['star_ids']), None
    return None, None


class PlanListResource(Resource):
    """Resource for listing and creating observing plans."""

    def get(self):
        """Get all plans."""
        return [_plan_to_dict(p) for p in Plan.query.order_by(Plan.created_at.desc()).all()]

    def post(self):
        """Create a new plan."""
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400
        if not json_data.get('name'):
            return {'message': 'Name is required'}, 400

        try:
            star_ids, _ = _normalise_star_ids(json_data)
        except (TypeError, ValueError):
            return {'message': 'stars must be a list of integer object ids'}, 400

        plan = Plan(
            name=json_data['name'],
            star_ids=star_ids,
            place_id=json_data.get('place_id'),
            instrument_id=json_data.get('instrument_id'),
            session_id=json_data.get('session_id'),
        )
        db.session.add(plan)
        db.session.commit()
        return _plan_to_dict(plan), 201


class PlanResource(Resource):
    """Resource for individual plan operations."""

    def get(self, plan_id):
        """Get a specific plan."""
        plan = Plan.query.get(plan_id)
        if not plan:
            return {'message': 'Plan not found'}, 404
        return _plan_to_dict(plan)

    def put(self, plan_id):
        """Update a specific plan."""
        plan = Plan.query.get(plan_id)
        if not plan:
            return {'message': 'Plan not found'}, 404

        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400

        if 'name' in json_data:
            plan.name = json_data['name']
        if 'stars' in json_data or 'star_ids' in json_data:
            try:
                star_ids, _ = _normalise_star_ids(json_data)
            except (TypeError, ValueError):
                return {'message': 'stars must be a list of integer object ids'}, 400
            plan.star_ids = star_ids
        for field in ('place_id', 'instrument_id', 'session_id'):
            if field in json_data:
                setattr(plan, field, json_data[field])

        db.session.commit()
        return _plan_to_dict(plan)

    def delete(self, plan_id):
        """Delete a specific plan."""
        plan = Plan.query.get(plan_id)
        if not plan:
            return {'message': 'Plan not found'}, 404
        db.session.delete(plan)
        db.session.commit()
        return {'message': 'Plan deleted successfully'}, 204


# =========================================================================
# Relationship Resources
# =========================================================================

class SessionObservationsResource(Resource):
    """Resource for retrieving observations recorded in a specific session."""

    def get(self, session_id):
        """Get all observations for a specific session."""
        session = Session.query.get(session_id)
        if not session:
            return {'message': 'Session not found'}, 404

        observations = Observation.query.filter_by(session_id=session_id).all()
        return [_observation_to_dict(obs) for obs in observations]


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
            result.append(_observation_to_dict(obs))

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
            result.append(_observation_to_dict(obs))

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
            result.append(_observation_to_dict(obs))

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
        return [_observation_to_dict(obs) for obs in observations]


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
