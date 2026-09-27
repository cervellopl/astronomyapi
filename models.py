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
    aavso_email = db.Column(db.String(255))
    aavso_password = db.Column(db.String(255))
    # Token for the apps.aavso.org v2 API (Authorization: Token <key>)
    aavso_api_key = db.Column(db.String(128))
    # Weather Underground personal weather station shown on the dashboard
    wu_station_id = db.Column(db.String(32))
    wu_api_key = db.Column(db.String(64))
    # Which dashboard widgets to show, comma-separated; NULL means "all of them"
    dashboard_widgets = db.Column(db.Text)

    def dashboard_widget_set(self, known):
        """Enabled widget ids, defaulting to everything for a new user."""
        raw = (self.dashboard_widgets or '').strip()
        if not raw:
            return set(known)
        return {w.strip() for w in raw.split(',') if w.strip() in known}
    backup_password = db.Column(db.String(255))
    backup_auto_enabled = db.Column(db.Boolean, default=False)
    backup_auto_interval = db.Column(db.String(20), default='weekly')
    backup_last_auto = db.Column(db.DateTime)
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
    # Exactly one place is the default observing site; the weather page and
    # other site-specific tools use it.
    is_default = db.Column(db.Boolean, default=False)

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

    # Multiple properties per observation (property/value pairs)
    properties = db.relationship(
        'ObservationProperty', backref='observation',
        cascade='all, delete-orphan', lazy=True
    )

    def __repr__(self):
        return f'<Observation {self.id} of {self.object}>'


class ObservationProperty(db.Model):
    """A single property/value pair attached to an observation.

    Allows an observation to carry any number of properties, superseding the
    legacy single prop1/prop1value columns (which are kept for back-compat).
    """

    __tablename__ = 'observation_properties'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    observation_id = db.Column(db.Integer, db.ForeignKey('observations.id'))
    property_id = db.Column(db.Integer, db.ForeignKey('properities.id'))
    value = db.Column(db.String(255))

    def __repr__(self):
        return f'<ObservationProperty obs={self.observation_id} prop={self.property_id}>'


class StarList(db.Model):
    """A saved set of stars to run the magnitude check over.

    Keeps object ids rather than names so a renamed object stays in the list.
    """

    __tablename__ = 'star_lists'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    star_ids = db.Column(db.Text)  # comma-separated Object ids
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def star_id_list(self):
        return [int(s) for s in (self.star_ids or '').split(',') if s.strip().isdigit()]

    def __repr__(self):
        return f'<StarList {self.id} {self.name}>'


class SkyCondition(db.Model):
    """One satellite reading of the sky over the observing site.

    Rows are keyed by the satellite frame rather than by when we polled, so a
    frame is stored once however often the dashboard asks for it.
    """

    __tablename__ = 'sky_conditions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    frame = db.Column(db.String(64), unique=True)     # IMGW frame timestamp
    observed_at = db.Column(db.DateTime, index=True)  # UTC, from the frame
    label = db.Column(db.String(120))
    clear = db.Column(db.Boolean, default=False)
    confident = db.Column(db.Boolean, default=True)
    rgb = db.Column(db.String(16))                    # sampled colour, '#rrggbb'
    sun_alt = db.Column(db.Float)
    place_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SkyCondition {self.observed_at} {self.label}>'


class StationReading(db.Model):
    """One observation from the personal weather station.

    Kept so the dashboard's live readings leave a history behind: rows are
    keyed by station and observation time, so re-reading the same observation
    stores it once.
    """

    __tablename__ = 'station_readings'
    __table_args__ = (db.UniqueConstraint('station', 'observed_at',
                                          name='uq_station_observed'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    station = db.Column(db.String(32), index=True)
    observed_at = db.Column(db.DateTime, index=True)   # station local time
    temp_c = db.Column(db.Float)
    dewpoint_c = db.Column(db.Float)
    spread_c = db.Column(db.Float)
    humidity = db.Column(db.Float)
    wind_kph = db.Column(db.Float)
    gust_kph = db.Column(db.Float)
    wind_dir = db.Column(db.Integer)
    pressure_hpa = db.Column(db.Float)
    precip_rate_mm = db.Column(db.Float)
    precip_total_mm = db.Column(db.Float)
    solar_wm2 = db.Column(db.Float)
    uv = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<StationReading {self.station} {self.observed_at} {self.temp_c}C>'


class Plan(db.Model):
    """Saved variable star observing plan.

    A plan stores the ordered list of variable star object ids (as a
    comma-separated string) plus shared defaults, so it can be re-run anytime.
    """

    __tablename__ = 'plans'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    star_ids = db.Column(db.Text)  # comma-separated Object ids, in order
    place_id = db.Column(db.Integer)
    instrument_id = db.Column(db.Integer)
    session_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def star_id_list(self):
        return [s for s in (self.star_ids or '').split(',') if s]

    def __repr__(self):
        return f'<Plan {self.id} {self.name}>'
