"""
Astronomy Observations API
==========================
A RESTful API for managing astronomical observations database.

This application provides a complete interface for:
- Managing instruments, celestial objects, observation places
- Recording and retrieving astronomical observations
- Handling observation properties and object types

Features:
- Full CRUD operations for all database entities
- Advanced filtering and search capabilities
- Relationship management between observations, objects, instruments, and locations
- Comprehensive data validation and error handling
- JSON-based RESTful interface

Dependencies:
- Flask: Web framework
- SQLAlchemy: ORM for database interactions
- Flask-RESTful: Extension for building REST APIs
- marshmallow: Object serialization/deserialization
- PyMySQL: MySQL database connector
"""

import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, validate
from werkzeug.middleware.proxy_fix import ProxyFix

# Initialize Flask app
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

# Configure database connection
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://username:password@localhost/astronomy_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False  # Preserve order of JSON keys in response

# Initialize extensions
db = SQLAlchemy(app)
api = Api(app)

# =============================================================================
# Database Models
# =============================================================================

class Type(db.Model):
    __tablename__ = 'types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    
    objects = db.relationship('Object', backref='object_type', lazy=True)
    
    def __repr__(self):
        return f'<Type {self.name}>'


class Property(db.Model):
    __tablename__ = 'properities'  # Maintaining original spelling from SQL
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    valueType = db.Column(db.String(255))
    
    observations = db.relationship('Observation', backref='property', lazy=True)
    
    def __repr__(self):
        return f'<Property {self.name}>'


class Place(db.Model):
    __tablename__ = 'places'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    lat = db.Column(db.String(255))
    lon = db.Column(db.String(255))
    alt = db.Column(db.String(255))
    timezone = db.Column(db.String(255))
    
    observations = db.relationship('Observation', backref='observation_place', lazy=True)
    
    def __repr__(self):
        return f'<Place {self.name}>'


class Instrument(db.Model):
    __tablename__ = 'instruments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    aperture = db.Column(db.String(255))
    power = db.Column(db.String(255))
    
    observations = db.relationship('Observation', backref='observation_instrument', lazy=True)
    
    def __repr__(self):
        return f'<Instrument {self.name}>'


class Object(db.Model):
    __tablename__ = 'objects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    desination = db.Column(db.String(255))  # Maintaining original spelling from SQL
    type = db.Column(db.Integer, db.ForeignKey('types.id'))
    props = db.Column(db.Text)
    
    observations = db.relationship('Observation', backref='observed_object', lazy=True)
    
    def __repr__(self):
        return f'<Object {self.name}>'


class Observation(db.Model):
    __tablename__ = 'observations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    object = db.Column(db.Integer, db.ForeignKey('objects.id'))
    place = db.Column(db.Integer, db.ForeignKey('places.id'))
    instrument = db.Column(db.Integer, db.ForeignKey('instruments.id'))
    datetime = db.Column(db.DateTime)
    observation = db.Column(db.String(255))
    prop1 = db.Column(db.Integer, db.ForeignKey('properities.id'))
    prop1value = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Observation {self.id} of {self.object}>'


# =============================================================================
# Schema Definitions
# =============================================================================

class TypeSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    
    class Meta:
        fields = ('id', 'name')


class PropertySchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    valueType = fields.String(required=True)
    
    class Meta:
        fields = ('id', 'name', 'valueType')


class PlaceSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    lat = fields.String(required=True)
    lon = fields.String(required=True)
    alt = fields.String()
    timezone = fields.String()
    
    class Meta:
        fields = ('id', 'name', 'lat', 'lon', 'alt', 'timezone')


class InstrumentSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    aperture = fields.String()
    power = fields.String()
    
    class Meta:
        fields = ('id', 'name', 'aperture', 'power')


class ObjectSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    desination = fields.String()
    type = fields.Integer(required=True)
    props = fields.String()
    
    class Meta:
        fields = ('id', 'name', 'desination', 'type', 'props')


class ObservationSchema(Schema):
    id = fields.Integer(dump_only=True)
    object = fields.Integer(required=True)
    place = fields.Integer(required=True)
    instrument = fields.Integer(required=True)
    datetime = fields.DateTime(required=True)
    observation = fields.String(required=True)
    prop1 = fields.Integer()
    prop1value = fields.String()
    
    class Meta:
        fields = ('id', 'object', 'place', 'instrument', 'datetime', 'observation', 'prop1', 'prop1value')


# Initialize schemas
type_schema = TypeSchema()
types_schema = TypeSchema(many=True)

property_schema = PropertySchema()
properties_schema = PropertySchema(many=True)

place_schema = PlaceSchema()
places_schema = PlaceSchema(many=True)

instrument_schema = InstrumentSchema()
instruments_schema = InstrumentSchema(many=True)

object_schema = ObjectSchema()
objects_schema = ObjectSchema(many=True)

observation_schema = ObservationSchema()
observations_schema = ObservationSchema(many=True)


# =============================================================================
# API Resources
# =============================================================================

class TypeListResource(Resource):
    def get(self):
        types = Type.query.all()
        return types_schema.dump(types)
    
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        try:
            data = type_schema.load(json_data)
        except Exception as e:
            return {'message': str(e)}, 422
        
        type_obj = Type(name=json_data['name'])
        
        db.session.add(type_obj)
        db.session.commit()
        
        return type_schema.dump(type_obj), 201


class TypeResource(Resource):
    def get(self, type_id):
        type_obj = Type.query.get_or_404(type_id)
        return type_schema.dump(type_obj)
    
    def put(self, type_id):
        type_obj = Type.query.get_or_404(type_id)
        json_data = request.get_json()
        
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        try:
            data = type_schema.load(json_data)
        except Exception as e:
            return {'message': str(e)}, 422
        
        type_obj.name = json_data['name']
        
        db.session.commit()
        
        return type_schema.dump(type_obj)
    
    def delete(self, type_id):
        type_obj = Type.query.get_or_404(type_id)
        db.session.delete(type_obj)
        db.session.commit()
        
        return '', 204


class PropertyListResource(Resource):
    def get(self):
        properties = Property.query.all()
        return properties_schema.dump(properties)
    
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        try:
            data = property_schema.load(json_data)
        except Exception as e:
            return {'message': str(e)}, 422
        
        property_obj = Property(
            id=json_data.get('id'),
            name=json_data['name'],
            valueType=json_data['valueType']
        )
        
        db.session.add(property_obj)
        db.session.commit()
        
        return property_schema.dump(property_obj), 201


class PropertyResource(Resource):
    def get(self, property_id):
        property_obj = Property.query.get_or_404(property_id)
        return property_schema.dump(property_obj)
    
    def put(self, property_id):
        property_obj = Property.query.get_or_404(property_id)
        json_data = request.get_json()
        
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        try:
            data = property_schema.load(json_data)
        except Exception as e:
            return {'message': str(e)}, 422
        
        property_obj.name = json_data['name']
        property_obj.valueType = json_data['valueType']
        
        db.session.commit()
        
        return property_schema.dump(property_obj)
    
    def delete(self, property_id):
        property_obj = Property.query.get_or_404(property_id)
        db.session.delete(property_obj)
        db.session.commit()
        
        return '', 204


class PlaceListResource(Resource):
    def get(self):
        places = Place.query.all()
        return places_schema.dump(places)
    
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        try:
            data = place_schema.load(json_data)
        except Exception as e:
            return {'message': str(e)}, 422
        
        place_obj = Place(
            name=json_data['name'],
            lat=json_data['lat'],
            lon=json_data['lon'],
            alt=json_data.get('alt'),
            timezone=json_data.get('timezone')
        )
        
        db.session.add(place_obj)
        db.session.commit()
        
        return place_schema.dump(place_obj), 201


class PlaceResource(Resource):
    def get(self, place_id):
        place_obj = Place.query.get_or_404(place_id)
        return place_schema.dump(place_obj)
    
    def put(self, place_id):
        place_obj = Place.query.get_or_404(place_id)
        json_data = request.get_json()
        
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        try:
            data = place_schema.load(json_data)
        except Exception as e:
            return {'message': str(e)}, 422
        
        place_obj.name = json_data['name']
        place_obj.lat = json_data['lat']
        place_obj.lon = json_data['lon']
        place_obj.alt = json_data.get('alt', place_obj.alt)
        place_obj.timezone = json_data.get('timezone', place_obj.timezone)
        
        db.session.commit()
        
        return place_schema.dump(place_obj)
    
    def delete(self, place_id):
        place_obj = Place.query.get_or_404(place_id)
        db.session.delete(place_obj)
        db.session.commit()
        
        return '', 204


class InstrumentListResource(Resource):
    def get(self):
        instruments = Instrument.query.all()
        return instruments_schema.dump(instruments)
    
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        try:
            data = instrument_schema.load(json_data)
        except Exception as e:
            return {'message': str(e)}, 422
        
        instrument_obj = Instrument(
            id=json_data.get('id'),
            name=json_data['name'],
            aperture=json_data.get('aperture'),
            power=json_data.get('power')
        )
        
        db.session.add(instrument_obj)
        db.session.commit()
        
        return instrument_schema.dump(instrument_obj), 201


class InstrumentResource(Resource):
    def get(self, instrument_id):
        instrument_obj = Instrument.query.get_or_404(instrument_id)
        return instrument_schema.dump(instrument_obj)
    
    def put(self, instrument_id):
        instrument_obj = Instrument.query.get_or_404(instrument_id)
        json_data = request.get_json()
        
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        try:
            data = instrument_schema.load(json_data)
        except Exception as e:
            return {'message': str(e)}, 422
        
        instrument_obj.name = json_data['name']
        instrument_obj.aperture = json_data.get('aperture', instrument_obj.aperture)
        instrument_obj.power = json_data.get('power', instrument_obj.power)
        
        db.session.commit()
        
        return instrument_schema.dump(instrument_obj)
    
    def delete(self, instrument_id):
        instrument_obj = Instrument.query.get_or_404(instrument_id)
        db.session.delete(instrument_obj)
        db.session.commit()
        
        return '', 204


class ObjectListResource(Resource):
    def get(self):
        objects = Object.query.all()
        return objects_schema.dump(objects)
    
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        try:
            data = object_schema.load(json_data)
        except Exception as e:
            return {'message': str(e)}, 422
        
        # Check if type exists
        type_obj = Type.query.get(json_data['type'])
        if not type_obj:
            return {'message': 'Invalid type ID'}, 400
        
        object_obj = Object(
            id=json_data.get('id'),
            name=json_data['name'],
            desination=json_data.get('desination'),
            type=json_data['type'],
            props=json_data.get('props')
        )
        
        db.session.add(object_obj)
        db.session.commit()
        
        return object_schema.dump(object_obj), 201


class ObjectResource(Resource):
    def get(self, object_id):
        object_obj = Object.query.get_or_404(object_id)
        return object_schema.dump(object_obj)
    
    def put(self, object_id):
        object_obj = Object.query.get_or_404(object_id)
        json_data = request.get_json()
        
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        try:
            data = object_schema.load(json_data)
        except Exception as e:
            return {'message': str(e)}, 422
        
        # Check if type exists if provided
        if 'type' in json_data:
            type_obj = Type.query.get(json_data['type'])
            if not type_obj:
                return {'message': 'Invalid type ID'}, 400
            object_obj.type = json_data['type']
        
        object_obj.name = json_data.get('name', object_obj.name)
        object_obj.desination = json_data.get('desination', object_obj.desination)
        object_obj.props = json_data.get('props', object_obj.props)
        
        db.session.commit()
        
        return object_schema.dump(object_obj)
    
    def delete(self, object_id):
        object_obj = Object.query.get_or_404(object_id)
        db.session.delete(object_obj)
        db.session.commit()
        
        return '', 204


class ObservationListResource(Resource):
    def get(self):
        observations = Observation.query.all()
        return observations_schema.dump(observations)
    
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        try:
            data = observation_schema.load(json_data)
        except Exception as e:
            return {'message': str(e)}, 422
        
        # Validate foreign keys
        object_obj = Object.query.get(json_data['object'])
        if not object_obj:
            return {'message': 'Invalid object ID'}, 400
        
        place_obj = Place.query.get(json_data['place'])
        if not place_obj:
            return {'message': 'Invalid place ID'}, 400
        
        instrument_obj = Instrument.query.get(json_data['instrument'])
        if not instrument_obj:
            return {'message': 'Invalid instrument ID'}, 400
        
        # Validate property if provided
        if 'prop1' in json_data and json_data['prop1']:
            property_obj = Property.query.get(json_data['prop1'])
            if not property_obj:
                return {'message': 'Invalid property ID'}, 400
        
        # Parse datetime
        try:
            observation_datetime = datetime.fromisoformat(json_data['datetime'].replace('Z', '+00:00'))
        except Exception:
            return {'message': 'Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}, 400
        
        observation_obj = Observation(
            object=json_data['object'],
            place=json_data['place'],
            instrument=json_data['instrument'],
            datetime=observation_datetime,
            observation=json_data['observation'],
            prop1=json_data.get('prop1'),
            prop1value=json_data.get('prop1value')
        )
        
        db.session.add(observation_obj)
        db.session.commit()
        
        return observation_schema.dump(observation_obj), 201


class ObservationResource(Resource):
    def get(self, observation_id):
        observation_obj = Observation.query.get_or_404(observation_id)
        return observation_schema.dump(observation_obj)
    
    def put(self, observation_id):
        observation_obj = Observation.query.get_or_404(observation_id)
        json_data = request.get_json()
        
        if not json_data:
            return {'message': 'No input data provided'}, 400
        
        try:
            data = observation_schema.load(json_data)
        except Exception as e:
            return {'message': str(e)}, 422
        
        # Validate foreign keys if provided
        if 'object' in json_data:
            object_obj = Object.query.get(json_data['object'])
            if not object_obj:
                return {'message': 'Invalid object ID'}, 400
            observation_obj.object = json_data['object']
        
        if 'place' in json_data:
            place_obj = Place.query.get(json_data['place'])
            if not place_obj:
                return {'message': 'Invalid place ID'}, 400
            observation_obj.place = json_data['place']
        
        if 'instrument' in json_data:
            instrument_obj = Instrument.query.get(json_data['instrument'])
            if not instrument_obj:
                return {'message': 'Invalid instrument ID'}, 400
            observation_obj.instrument = json_data['instrument']
        
        if 'prop1' in json_data and json_data['prop1']:
            property_obj = Property.query.get(json_data['prop1'])
            if not property_obj:
                return {'message': 'Invalid property ID'}, 400
            observation_obj.prop1 = json_data['prop1']
        
        # Parse datetime if provided
        if 'datetime' in json_data:
            try:
                observation_datetime = datetime.fromisoformat(json_data['datetime'].replace('Z', '+00:00'))
                observation_obj.datetime = observation_datetime
            except Exception:
                return {'message': 'Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}, 400
        
        observation_obj.observation = json_data.get('observation', observation_obj.observation)
        observation_obj.prop1value = json_data.get('prop1value', observation_obj.prop1value)
        
        db.session.commit()
        
        return observation_schema.dump(observation_obj)
    
    def delete(self, observation_id):
        observation_obj = Observation.query.get_or_404(observation_id)
        db.session.delete(observation_obj)
        db.session.commit()
        
        return '', 204


# Advanced query endpoints
class ObjectObservationsResource(Resource):
    def get(self, object_id):
        # Get all observations for a specific object
        observations = Observation.query.filter_by(object=object_id).all()
        return observations_schema.dump(observations)


class PlaceObservationsResource(Resource):
    def get(self, place_id):
        # Get all observations made at a specific place
        observations = Observation.query.filter_by(place=place_id).all()
        return observations_schema.dump(observations)


class InstrumentObservationsResource(Resource):
    def get(self, instrument_id):
        # Get all observations made with a specific instrument
        observations = Observation.query.filter_by(instrument=instrument_id).all()
        return observations_schema.dump(observations)


class ObservationSearchResource(Resource):
    def get(self):
        # Get parameters
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
            query = query.filter(Observation.object == object_id)
        
        if place_id:
            query = query.filter(Observation.place == place_id)
        
        if instrument_id:
            query = query.filter(Observation.instrument == instrument_id)
        
        # Execute query
        observations = query.all()
        
        return observations_schema.dump(observations)


# =============================================================================
# API Routes
# =============================================================================

# Register resources
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

# Advanced query endpoints
api.add_resource(ObjectObservationsResource, '/api/objects/<int:object_id>/observations')
api.add_resource(PlaceObservationsResource, '/api/places/<int:place_id>/observations')
api.add_resource(InstrumentObservationsResource, '/api/instruments/<int:instrument_id>/observations')
api.add_resource(ObservationSearchResource, '/api/observations/search')

# Root endpoint - API documentation
@app.route('/')
def index():
    """API documentation endpoint"""
    return jsonify({
        'api': 'Astronomy Observations API',
        'version': '1.0',
        'description': 'API for managing astronomical observations database',
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


if __name__ == '__main__':
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Run the application
    app.run(debug=True)
