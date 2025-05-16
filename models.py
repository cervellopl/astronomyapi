"""
Astronomy API Models
===================
Database models for the Astronomy Observations API.

This module defines the SQLAlchemy models that represent the database schema
from the original SQL file.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Import db from the config module
from config import db


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
    aperture = db.Column(db.String(255))
    power = db.Column(db.String(255))
    
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


class Observation(db.Model):
    """Astronomical observation model."""
    
    __tablename__ = 'observations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    object = db.Column(db.Integer, db.ForeignKey('objects.id'))
    place = db.Column(db.Integer, db.ForeignKey('places.id'))
    instrument = db.Column(db.Integer, db.ForeignKey('instruments.id'))
    datetime = db.Column(db.DateTime, default=datetime.utcnow)
    observation = db.Column(db.String(255))
    prop1 = db.Column(db.Integer, db.ForeignKey('properities.id'))
    prop1value = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Observation {self.id} of {self.object}>'
