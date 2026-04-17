"""
Astronomy API Models
===================
Database models for the Astronomy Observations API.

This module defines the SQLAlchemy models that represent the database schema
from the original SQL file.
"""

from datetime import datetime

# Import db from the database module
from database import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    """User model for authentication."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255))
    password_hash = db.Column(db.String(255), nullable=False)
    postal_address = db.Column(db.Text)
    aavso_code = db.Column(db.String(20))
    icq_code = db.Column(db.String(20))
    default_timezone = db.Column(db.String(100))
    cobs_username = db.Column(db.String(150))
    cobs_password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Type(db.Model):
    """Celestial object type model."""
    
    __tablename__ = 'types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    
    objects = db.relationship('Object', backref='object_type', lazy=True)
    
    def __repr__(self):
        return f'<Type {self.name}>'


class Property(db.Model):
    """Observation property model."""
    
    __tablename__ = 'properities'  # Maintaining original spelling from SQL
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    valueType = db.Column(db.String(255))
    
    observations = db.relationship('Observation', backref='property', lazy=True)
    
    def __repr__(self):
        return f'<Property {self.name}>'


class Place(db.Model):
    """Observation place model."""
    
    __tablename__ = 'places'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    alias = db.Column(db.String(255))
    lat = db.Column(db.String(255))
    lon = db.Column(db.String(255))
    alt = db.Column(db.String(255))
    timezone = db.Column(db.String(255))
    
    observations = db.relationship('Observation', backref='observation_place', lazy=True)
    
    def __repr__(self):
        return f'<Place {self.name}>'


class Instrument(db.Model):
    """Astronomical instrument model."""
    
    __tablename__ = 'instruments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    instrument_type = db.Column(db.String(255))
    aperture = db.Column(db.String(255))
    power = db.Column(db.String(255))
    eyepiece = db.Column(db.String(255))

    observations = db.relationship('Observation', backref='observation_instrument', lazy=True)
    
    def __repr__(self):
        return f'<Instrument {self.name}>'


class Object(db.Model):
    """Celestial object model."""
    
    __tablename__ = 'objects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    desination = db.Column(db.String(255))  # Maintaining original spelling from SQL
    type = db.Column(db.Integer, db.ForeignKey('types.id'))
    props = db.Column(db.Text)
    
    observations = db.relationship('Observation', backref='observed_object', lazy=True)
    
    def __repr__(self):
        return f'<Object {self.name}>'


class Session(db.Model):
    """Observation session model."""

    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number = db.Column(db.String(20))  # format "n/yyyy"
    start_datetime = db.Column(db.DateTime)
    end_datetime = db.Column(db.DateTime)
    cloud_percentage = db.Column(db.Integer)
    cloud_type = db.Column(db.String(255))
    light_pollution = db.Column(db.Integer)  # 1-10 scale
    limiting_magnitude = db.Column(db.Float)
    moon_phase = db.Column(db.String(50))
    moon_altitude = db.Column(db.Float)
    instrument = db.Column(db.Integer, db.ForeignKey('instruments.id'))

    session_instrument = db.relationship('Instrument', backref='sessions', lazy=True)
    observations = db.relationship('Observation', backref='observation_session', lazy=True)

    def __repr__(self):
        return f'<Session {self.number}>'


class Observation(db.Model):
    """Astronomical observation model."""

    __tablename__ = 'observations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    object = db.Column(db.Integer, db.ForeignKey('objects.id'))
    place = db.Column(db.Integer, db.ForeignKey('places.id'))
    instrument = db.Column(db.Integer, db.ForeignKey('instruments.id'))
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    datetime = db.Column(db.DateTime, default=datetime.utcnow)
    observation = db.Column(db.String(255))
    prop1 = db.Column(db.Integer, db.ForeignKey('properities.id'))
    prop1value = db.Column(db.String(255))

    def __repr__(self):
        return f'<Observation {self.id} of {self.object}>'
