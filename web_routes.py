"""
Create a complete new web_routes.py with proper handling
"""

def create_new_web_routes():
    """Create a complete new web_routes.py"""
    print("Creating new web_routes.py...")
    
    content = '''"""
Web interface routes for Astronomy Observations
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Type, Property, Place, Instrument, Object, Observation
from database import db
from datetime import datetime

web = Blueprint('web', __name__)

# ============================================================================
# DASHBOARD
# ============================================================================

@web.route('/')
def dashboard():
    """Dashboard view"""
    try:
        # Get counts
        counts = {
            'types': Type.query.count(),
            'properties': Property.query.count(),
            'places': Place.query.count(),
            'instruments': Instrument.query.count(),
            'objects': Object.query.count(),
            'observations': Observation.query.count()
        }
        
        # Get recent observations
        recent_observations = Observation.query.order_by(Observation.datetime.desc()).limit(10).all()
        
        return render_template('dashboard.html', counts=counts, recent_observations=recent_observations)
    except Exception as e:
        print(f"Dashboard error: {str(e)}")
        return render_template('dashboard.html', counts={}, recent_observations=[])

# ============================================================================
# OBJECTS
# ============================================================================

@web.route('/objects')
def list_objects():
    """List all objects"""
    try:
        objects = Object.query.all()
        return render_template('objects/list.html', objects=objects)
    except Exception as e:
        flash(f'Error loading objects: {str(e)}', 'danger')
        return render_template('objects/list.html', objects=[])

@web.route('/objects/add', methods=['GET', 'POST'])
def add_object():
    """Add a new object"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            desination = request.form.get('desination')
            object_type = request.form.get('type')
            props = request.form.get('props')
            
            # Create new object
            new_object = Object(
                name=name,
                desination=desination,
                type=int(object_type),
                props=props
            )
            
            db.session.add(new_object)
            db.session.commit()
            
            flash(f'Object "{name}" added successfully!', 'success')
            return redirect(url_for('web.list_objects'))
        except Exception as e:
            flash(f'Error adding object: {str(e)}', 'danger')
            db.session.rollback()
    
    # Get types for the form
    try:
        types = Type.query.all()
    except:
        types = []
    
    return render_template('objects/add.html', types=types)

# ============================================================================
# OBSERVATIONS
# ============================================================================

@web.route('/observations')
def list_observations():
    """List all observations"""
    try:
        observations = Observation.query.order_by(Observation.datetime.desc()).all()
        return render_template('observations/list.html', observations=observations)
    except Exception as e:
        flash(f'Error loading observations: {str(e)}', 'danger')
        return render_template('observations/list.html', observations=[])

@web.route('/observations/add', methods=['GET', 'POST'])
def add_observation():
    """Add a new observation"""
    if request.method == 'POST':
        try:
            # Get basic form data
            object_id = request.form.get('object')
            place_id = request.form.get('place')
            instrument_id = request.form.get('instrument')
            datetime_str = request.form.get('datetime')
            observation_text = request.form.get('observation')
            
            # Parse datetime
            obs_datetime = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            
            # Create new observation
            new_observation = Observation(
                object=int(object_id),
                place=int(place_id),
                instrument=int(instrument_id),
                datetime=obs_datetime,
                observation=observation_text
            )
            
            # Handle additional fields (property)
            prop1 = request.form.get('prop1')
            prop1value = request.form.get('prop1value')
            if prop1 and prop1value:
                new_observation.prop1 = int(prop1)
                new_observation.prop1value = prop1value
            
            db.session.add(new_observation)
            db.session.commit()
            
            flash('Observation added successfully!', 'success')
            return redirect(url_for('web.list_observations'))
        except Exception as e:
            flash(f'Error adding observation: {str(e)}', 'danger')
            db.session.rollback()
    
    # Get data for the form
    try:
        objects = Object.query.all()
        places = Place.query.all()
        instruments = Instrument.query.all()
        properties = Property.query.all()
    except:
        objects = []
        places = []
        instruments = []
        properties = []
    
    return render_template('observations/add.html', 
                         objects=objects, 
                         places=places, 
                         instruments=instruments,
                         properties=properties)

# ============================================================================
# INSTRUMENTS
# ============================================================================

@web.route('/instruments')
def list_instruments():
    """List all instruments"""
    try:
        instruments = Instrument.query.all()
        return render_template('instruments/list.html', instruments=instruments)
    except Exception as e:
        flash(f'Error loading instruments: {str(e)}', 'danger')
        return render_template('instruments/list.html', instruments=[])

@web.route('/instruments/add', methods=['GET', 'POST'])
def add_instrument():
    """Add a new instrument"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            aperture = request.form.get('aperture')
            power = request.form.get('power')
            
            # Find the highest existing ID and add 1
            max_id = db.session.query(db.func.max(Instrument.id)).scalar() or 0
            
            # Create new instrument
            new_instrument = Instrument(
                id=max_id + 1,
                name=name,
                aperture=aperture,
                power=power
            )
            
            db.session.add(new_instrument)
            db.session.commit()
            
            flash(f'Instrument "{name}" added successfully!', 'success')
            return redirect(url_for('web.list_instruments'))
        except Exception as e:
            flash(f'Error adding instrument: {str(e)}', 'danger')
            db.session.rollback()
    
    return render_template('instruments/add.html')

# ============================================================================
# PLACES
# ============================================================================

@web.route('/places')
def list_places():
    """List all places"""
    try:
        places = Place.query.all()
        return render_template('places/list.html', places=places)
    except Exception as e:
        flash(f'Error loading places: {str(e)}', 'danger')
        return render_template('places/list.html', places=[])

@web.route('/places/add', methods=['GET', 'POST'])
def add_place():
    """Add a new place"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            lat = request.form.get('lat')
            lon = request.form.get('lon')
            alt = request.form.get('alt')
            timezone = request.form.get('timezone')
            
            # Create new place
            new_place = Place(
                name=name,
                lat=lat,
                lon=lon,
                alt=alt,
                timezone=timezone
            )
            
            db.session.add(new_place)
            db.session.commit()
            
            flash(f'Place "{name}" added successfully!', 'success')
            return redirect(url_for('web.list_places'))
        except Exception as e:
            flash(f'Error adding place: {str(e)}', 'danger')
            db.session.rollback()
    
    return render_template('places/add.html')

# ============================================================================
# TYPES
# ============================================================================

@web.route('/types')
def list_types():
    """List all types"""
    try:
        types = Type.query.all()
        return render_template('types/list.html', types=types)
    except Exception as e:
        flash(f'Error loading types: {str(e)}', 'danger')
        return render_template('types/list.html', types=[])

@web.route('/types/add', methods=['GET', 'POST'])
def add_type():
    """Add a new type"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            
            # Find the highest existing ID and add 1
            max_id = db.session.query(db.func.max(Type.id)).scalar() or 0
            
            # Create new type
            new_type = Type(
                id=max_id + 1,
                name=name
            )
            
            db.session.add(new_type)
            db.session.commit()
            
            flash(f'Type "{name}" added successfully!', 'success')
            return redirect(url_for('web.list_types'))
        except Exception as e:
            flash(f'Error adding type: {str(e)}', 'danger')
            db.session.rollback()
    
    return render_template('types/add.html')

# ============================================================================
# PROPERTIES
# ============================================================================

@web.route('/properties')
def list_properties():
    """List all properties"""
    try:
        properties = Property.query.all()
        return render_template('properties/list.html', properties=properties)
    except Exception as e:
        flash(f'Error loading properties: {str(e)}', 'danger')
        return render_template('properties/list.html', properties=[])

@web.route('/properties/add', methods=['GET', 'POST'])
def add_property():
    """Add a new property"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            value_type = request.form.get('valueType')
            
            # Find the highest existing ID and add 1
            max_id = db.session.query(db.func.max(Property.id)).scalar() or 0
            
            # Create new property
            new_property = Property(
                id=max_id + 1,
                name=name,
                valueType=value_type
            )
            
            db.session.add(new_property)
            db.session.commit()
            
            flash(f'Property "{name}" added successfully!', 'success')
            return redirect(url_for('web.list_properties'))
        except Exception as e:
            flash(f'Error adding property: {str(e)}', 'danger')
            db.session.rollback()
    
    return render_template('properties/add.html')

# ============================================================================
# SEARCH
# ============================================================================

@web.route('/search', methods=['GET', 'POST'])
def search_observations():
    """Search observations"""
    search_executed = False
    observations = []
    
    if request.method == 'POST':
        search_executed = True
        try:
            # Get search parameters
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            object_id = request.form.get('object')
            place_id = request.form.get('place')
            instrument_id = request.form.get('instrument')
            
            # Build query
            query = Observation.query
            
            if start_date:
                start_dt = datetime.fromisoformat(start_date)
                query = query.filter(Observation.datetime >= start_dt)
            
            if end_date:
                end_dt = datetime.fromisoformat(end_date)
                query = query.filter(Observation.datetime <= end_dt)
            
            if object_id and object_id != 'all':
                query = query.filter(Observation.object == int(object_id))
            
            if place_id and place_id != 'all':
                query = query.filter(Observation.place == int(place_id))
            
            if instrument_id and instrument_id != 'all':
                query = query.filter(Observation.instrument == int(instrument_id))
            
            observations = query.order_by(Observation.datetime.desc()).all()
        except Exception as e:
            flash(f'Error searching: {str(e)}', 'danger')
    
    # Get data for filters
    try:
        objects = Object.query.all()
        places = Place.query.all()
        instruments = Instrument.query.all()
    except:
        objects = []
        places = []
        instruments = []
    
    return render_template('search.html', 
                         search_executed=search_executed,
                         observations=observations,
                         objects=objects,
                         places=places,
                         instruments=instruments)
'''
    
    with open('web_routes.py', 'w') as f:
        f.write(content)
    
    print("Created new web_routes.py!")
    return True

if __name__ == '__main__':
    create_new_web_routes()