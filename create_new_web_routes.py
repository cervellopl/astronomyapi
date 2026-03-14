"""
Create a complete new web_routes.py with proper ID handling
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
from sqlalchemy import func
from import_comets_mpc import import_comets_from_mpc, sync_comets_from_mpc

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
            
            # Find the highest existing ID and add 1
            max_id = db.session.query(func.max(Object.id)).scalar()
            new_id = (max_id or 0) + 1
            
            # Create new object with explicit ID
            new_object = Object(
                id=new_id,
                name=name,
                desination=desination,
                type=int(object_type),
                props=props if props else None
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
            
            # Create new observation (id is AUTO_INCREMENT)
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
            
            # Handle AAVSO variable star fields
            vs_magnitude = request.form.get('vs_magnitude')
            if vs_magnitude:
                # Store AAVSO data in observation text or separate fields
                aavso_data = []
                aavso_data.append(f"Magnitude: {vs_magnitude}")
                
                vs_uncertainty = request.form.get('vs_uncertainty')
                if vs_uncertainty:
                    aavso_data.append(f"Uncertainty: {vs_uncertainty}")
                
                vs_comp1 = request.form.get('vs_comp_star1')
                if vs_comp1:
                    aavso_data.append(f"Comp1: {vs_comp1}")
                
                vs_comp2 = request.form.get('vs_comp_star2')
                if vs_comp2:
                    aavso_data.append(f"Comp2: {vs_comp2}")
                
                vs_check = request.form.get('vs_check_star')
                if vs_check:
                    aavso_data.append(f"Check: {vs_check}")
                
                vs_chart = request.form.get('vs_chart')
                if vs_chart:
                    aavso_data.append(f"Chart: {vs_chart}")
                
                vs_band = request.form.get('vs_band')
                if vs_band:
                    aavso_data.append(f"Band: {vs_band}")
                
                vs_observer = request.form.get('vs_observer_code')
                if vs_observer:
                    aavso_data.append(f"Observer: {vs_observer}")
                
                vs_method = request.form.get('vs_method')
                if vs_method:
                    aavso_data.append(f"Method: {vs_method}")
                
                # Append AAVSO data to observation text
                if aavso_data:
                    new_observation.observation += " [AAVSO: " + ", ".join(aavso_data) + "]"
            
            # Handle COBS comet fields
            comet_magnitude = request.form.get('comet_magnitude')
            if comet_magnitude:
                # Store COBS data in observation text
                cobs_data = []
                cobs_data.append(f"m1: {comet_magnitude}")
                
                coma_diameter = request.form.get('coma_diameter')
                if coma_diameter:
                    cobs_data.append(f"Coma: {coma_diameter}")
                
                dc = request.form.get('degree_condensation')
                if dc:
                    cobs_data.append(f"DC: {dc}")
                
                tail_length = request.form.get('tail_length')
                if tail_length:
                    cobs_data.append(f"Tail: {tail_length}")
                
                tail_pa = request.form.get('tail_pa')
                if tail_pa:
                    cobs_data.append(f"PA: {tail_pa}")
                
                ref_star = request.form.get('reference_star')
                if ref_star:
                    cobs_data.append(f"Ref: {ref_star}")
                
                sky = request.form.get('sky_conditions')
                if sky:
                    cobs_data.append(f"Sky: {sky}")
                
                comet_method = request.form.get('comet_method')
                if comet_method:
                    cobs_data.append(f"Method: {comet_method}")
                
                # Append COBS data to observation text
                if cobs_data:
                    new_observation.observation += " [COBS: " + ", ".join(cobs_data) + "]"
            
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
            max_id = db.session.query(func.max(Instrument.id)).scalar()
            new_id = (max_id or 0) + 1
            
            # Create new instrument with explicit ID
            new_instrument = Instrument(
                id=new_id,
                name=name,
                aperture=aperture if aperture else None,
                power=power if power else None
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
            
            # Create new place (id is AUTO_INCREMENT)
            new_place = Place(
                name=name,
                lat=lat,
                lon=lon,
                alt=alt if alt else None,
                timezone=timezone if timezone else None
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
            max_id = db.session.query(func.max(Type.id)).scalar()
            new_id = (max_id or 0) + 1
            
            # Create new type with explicit ID
            new_type = Type(
                id=new_id,
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
            max_id = db.session.query(func.max(Property.id)).scalar()
            new_id = (max_id or 0) + 1
            
            # Create new property with explicit ID
            new_property = Property(
                id=new_id,
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

# ============================================================================
# COMET IMPORT
# ============================================================================

@web.route('/comets/import', methods=['GET', 'POST'])
def import_comets():
    """Import comets from Minor Planet Center"""
    if request.method == 'POST':
        try:
            action = request.form.get('action')
            max_comets = request.form.get('max_comets')
            
            # Convert max_comets to int or None
            if max_comets:
                try:
                    max_comets = int(max_comets)
                except:
                    max_comets = None
            else:
                max_comets = None
            
            if action == 'import':
                stats = import_comets_from_mpc(max_comets=max_comets, update_existing=False)
                flash(f"Import complete! Added {stats.get('added', 0)} comets, skipped {stats.get('skipped', 0)}", 'success')
            elif action == 'sync':
                stats = sync_comets_from_mpc()
                flash(f"Sync complete! Added {stats.get('added', 0)} comets, updated {stats.get('updated', 0)}", 'success')
            
            return redirect(url_for('web.list_objects'))
        except Exception as e:
            flash(f'Error importing comets: {str(e)}', 'danger')
    
    # Get current comet count
    try:
        comet_type = Type.query.filter_by(name='Comet').first()
        if comet_type:
            comet_count = Object.query.filter_by(type=comet_type.id).count()
        else:
            comet_count = 0
    except:
        comet_count = 0
    
    return render_template('comets/import.html', comet_count=comet_count)
'''
    
    with open('web_routes.py', 'w') as f:
        f.write(content)
    
    print("Created new web_routes.py with proper ID handling!")
    return True

if __name__ == '__main__':
    create_new_web_routes()