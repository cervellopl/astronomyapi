"""
Create a complete new web_routes.py with proper ID handling
"""

def create_new_web_routes():
    """Create a complete new web_routes.py"""
    print("Creating new web_routes.py...")
    
    content = '''"""
Web interface routes for Astronomy Observations
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import Type, Property, Place, Instrument, Object, Observation, Session, User
from database import db
from datetime import datetime
from sqlalchemy import func
import requests as http_requests
from import_comets_mpc import import_comets_from_mpc, sync_comets_from_mpc
from import_vsx import import_vsx_stars, sync_vsx_stars
from import_simbad import search_simbad, lookup_simbad_object, import_simbad_object

web = Blueprint('web', __name__)

# ============================================================================
# AUTHENTICATION
# ============================================================================

@web.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('web.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('web.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('auth/login.html')

@web.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('web.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password != password2:
            flash('Passwords do not match.', 'danger')
        elif len(password) < 4:
            flash('Password must be at least 4 characters.', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('web.login'))

    return render_template('auth/register.html')

@web.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('web.login'))

@web.route('/settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    """User settings page"""
    if request.method == 'POST':
        try:
            action = request.form.get('action')

            if action == 'update_profile':
                current_user.email = request.form.get('email', '').strip() or None
                current_user.postal_address = request.form.get('postal_address', '').strip() or None
                current_user.aavso_code = request.form.get('aavso_code', '').strip() or None
                current_user.icq_code = request.form.get('icq_code', '').strip() or None
                current_user.default_timezone = request.form.get('default_timezone', '').strip() or None
                db.session.commit()
                flash('Profile updated successfully!', 'success')

            elif action == 'change_password':
                current_password = request.form.get('current_password')
                new_password = request.form.get('new_password')
                new_password2 = request.form.get('new_password2')

                if not current_user.check_password(current_password):
                    flash('Current password is incorrect.', 'danger')
                elif new_password != new_password2:
                    flash('New passwords do not match.', 'danger')
                elif len(new_password) < 4:
                    flash('New password must be at least 4 characters.', 'danger')
                else:
                    current_user.set_password(new_password)
                    db.session.commit()
                    flash('Password changed successfully!', 'success')

            return redirect(url_for('web.user_settings'))
        except Exception as e:
            flash(f'Error updating settings: {str(e)}', 'danger')
            db.session.rollback()

    return render_template('auth/settings.html')

# ============================================================================
# DASHBOARD
# ============================================================================

@web.route('/')
@login_required
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
            'observations': Observation.query.count(),
            'sessions': Session.query.count()
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
@login_required
def list_objects():
    """List all objects"""
    try:
        objects = Object.query.all()
        return render_template('objects/list.html', objects=objects)
    except Exception as e:
        flash(f'Error loading objects: {str(e)}', 'danger')
        return render_template('objects/list.html', objects=[])

@web.route('/objects/add', methods=['GET', 'POST'])
@login_required
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
@login_required
def list_observations():
    """List all observations"""
    try:
        observations = Observation.query.order_by(Observation.datetime.desc()).all()
        return render_template('observations/list.html', observations=observations)
    except Exception as e:
        flash(f'Error loading observations: {str(e)}', 'danger')
        return render_template('observations/list.html', observations=[])

@web.route('/observations/add', methods=['GET', 'POST'])
@login_required
def add_observation():
    """Add a new observation"""
    if request.method == 'POST':
        try:
            # Get basic form data
            object_id = request.form.get('object')
            place_id = request.form.get('place')
            instrument_id = request.form.get('instrument')
            session_id = request.form.get('session')
            datetime_str = request.form.get('datetime')
            observation_text = request.form.get('observation')

            # Parse datetime
            obs_datetime = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))

            # Create new observation (id is AUTO_INCREMENT)
            new_observation = Observation(
                object=int(object_id),
                place=int(place_id),
                instrument=int(instrument_id),
                session_id=int(session_id) if session_id else None,
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
        sessions = Session.query.order_by(Session.start_datetime.desc()).all()
    except:
        objects = []
        places = []
        instruments = []
        properties = []
        sessions = []

    return render_template('observations/add.html',
                         objects=objects,
                         places=places,
                         instruments=instruments,
                         properties=properties,
                         sessions=sessions)

# ============================================================================
# INSTRUMENTS
# ============================================================================

@web.route('/instruments')
@login_required
def list_instruments():
    """List all instruments"""
    try:
        instruments = Instrument.query.all()
        return render_template('instruments/list.html', instruments=instruments)
    except Exception as e:
        flash(f'Error loading instruments: {str(e)}', 'danger')
        return render_template('instruments/list.html', instruments=[])

@web.route('/instruments/add', methods=['GET', 'POST'])
@login_required
def add_instrument():
    """Add a new instrument"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            instrument_type = request.form.get('instrument_type')
            aperture = request.form.get('aperture')
            power = request.form.get('power')
            eyepiece = request.form.get('eyepiece')

            # Find the highest existing ID and add 1
            max_id = db.session.query(func.max(Instrument.id)).scalar()
            new_id = (max_id or 0) + 1

            # Create new instrument with explicit ID
            new_instrument = Instrument(
                id=new_id,
                name=name,
                instrument_type=instrument_type if instrument_type else None,
                aperture=aperture if aperture else None,
                power=power if power else None,
                eyepiece=eyepiece if eyepiece else None
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
@login_required
def list_places():
    """List all places"""
    try:
        places = Place.query.all()
        return render_template('places/list.html', places=places)
    except Exception as e:
        flash(f'Error loading places: {str(e)}', 'danger')
        return render_template('places/list.html', places=[])

@web.route('/places/add', methods=['GET', 'POST'])
@login_required
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
@login_required
def list_types():
    """List all types"""
    try:
        types = Type.query.all()
        return render_template('types/list.html', types=types)
    except Exception as e:
        flash(f'Error loading types: {str(e)}', 'danger')
        return render_template('types/list.html', types=[])

@web.route('/types/add', methods=['GET', 'POST'])
@login_required
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
@login_required
def list_properties():
    """List all properties"""
    try:
        properties = Property.query.all()
        return render_template('properties/list.html', properties=properties)
    except Exception as e:
        flash(f'Error loading properties: {str(e)}', 'danger')
        return render_template('properties/list.html', properties=[])

@web.route('/properties/add', methods=['GET', 'POST'])
@login_required
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
# SESSIONS
# ============================================================================

@web.route('/sessions')
@login_required
def list_sessions():
    """List all sessions"""
    try:
        sessions = Session.query.order_by(Session.start_datetime.desc()).all()
        return render_template('sessions/list.html', sessions=sessions)
    except Exception as e:
        flash(f'Error loading sessions: {str(e)}', 'danger')
        return render_template('sessions/list.html', sessions=[])

@web.route('/sessions/<int:session_id>')
@login_required
def view_session(session_id):
    """View a single session with its observations"""
    try:
        session = Session.query.get_or_404(session_id)
        observations = Observation.query.filter_by(session_id=session_id).order_by(Observation.datetime).all()
        return render_template('sessions/view.html', session=session, observations=observations)
    except Exception as e:
        flash(f'Error loading session: {str(e)}', 'danger')
        return redirect(url_for('web.list_sessions'))

@web.route('/sessions/add', methods=['GET', 'POST'])
@login_required
def add_session():
    """Add a new session"""
    if request.method == 'POST':
        try:
            number = request.form.get('number')
            start_datetime_str = request.form.get('start_datetime')
            end_datetime_str = request.form.get('end_datetime')
            cloud_percentage = request.form.get('cloud_percentage')
            cloud_type = request.form.get('cloud_type')
            light_pollution = request.form.get('light_pollution')
            limiting_magnitude = request.form.get('limiting_magnitude')
            moon_phase = request.form.get('moon_phase')
            moon_altitude = request.form.get('moon_altitude')
            instrument_id = request.form.get('instrument')

            start_dt = datetime.fromisoformat(start_datetime_str.replace('Z', '+00:00')) if start_datetime_str else None
            end_dt = datetime.fromisoformat(end_datetime_str.replace('Z', '+00:00')) if end_datetime_str else None

            new_session = Session(
                number=number,
                start_datetime=start_dt,
                end_datetime=end_dt,
                cloud_percentage=int(cloud_percentage) if cloud_percentage else None,
                cloud_type=cloud_type if cloud_type else None,
                light_pollution=int(light_pollution) if light_pollution else None,
                limiting_magnitude=float(limiting_magnitude) if limiting_magnitude else None,
                moon_phase=moon_phase if moon_phase else None,
                moon_altitude=float(moon_altitude) if moon_altitude else None,
                instrument=int(instrument_id) if instrument_id else None
            )

            db.session.add(new_session)
            db.session.commit()

            flash(f'Session "{number}" added successfully!', 'success')
            return redirect(url_for('web.list_sessions'))
        except Exception as e:
            flash(f'Error adding session: {str(e)}', 'danger')
            db.session.rollback()

    try:
        instruments = Instrument.query.all()
    except:
        instruments = []

    return render_template('sessions/add.html', instruments=instruments)

# ============================================================================
# SEARCH
# ============================================================================

@web.route('/search', methods=['GET', 'POST'])
@login_required
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
# AAVSO VSP CHARTS - Local download and storage
# ============================================================================

import os, re

CHARTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'charts')

VSP_SCALES = [
    {'key': 'A',  'fov': 180, 'label': 'A (3 deg)'},
    {'key': 'AB', 'fov': 120, 'label': 'AB (2 deg)'},
    {'key': 'B',  'fov': 60,  'label': 'B (1 deg)'},
    {'key': 'C',  'fov': 20,  'label': 'C (20 arcmin)'},
    {'key': 'D',  'fov': 10,  'label': 'D (10 arcmin)'},
    {'key': 'E',  'fov': 5,   'label': 'E (5 arcmin)'},
    {'key': 'F',  'fov': 2,   'label': 'F (2 arcmin)'},
]

def _safe_dirname(star_name):
    """Convert star name to safe directory name"""
    return re.sub(r'[^a-zA-Z0-9_\\-]', '_', star_name.strip())

def _get_local_charts(star_name):
    """Get list of locally stored charts for a star"""
    safe = _safe_dirname(star_name)
    star_dir = os.path.join(CHARTS_DIR, safe)
    charts = []
    if os.path.isdir(star_dir):
        for s in VSP_SCALES:
            png = os.path.join(star_dir, f"{s['key']}.png")
            meta = os.path.join(star_dir, f"{s['key']}.meta")
            if os.path.isfile(png):
                chartid = ''
                if os.path.isfile(meta):
                    with open(meta) as mf:
                        chartid = mf.read().strip()
                charts.append({
                    'scale': s['key'],
                    'label': s['label'],
                    'fov': s['fov'],
                    'chartid': chartid,
                    'image_url': f"/static/charts/{safe}/{s['key']}.png",
                    'local': True,
                    'size': os.path.getsize(png),
                })
    return charts

@web.route('/vsp/local/<path:star_name>')
@login_required
def vsp_local_charts(star_name):
    """Get locally stored charts for a star"""
    charts = _get_local_charts(star_name)
    return jsonify({'star': star_name, 'charts': charts})

@web.route('/vsp/download', methods=['POST'])
@login_required
def vsp_download_chart():
    """Download a single chart from AAVSO VSP and store locally"""
    star_name = request.form.get('star_name', '').strip()
    scale_key = request.form.get('scale', '').strip()

    if not star_name or not scale_key:
        return jsonify({'error': 'Missing star_name or scale'}), 400

    # Find scale info
    scale_info = None
    for s in VSP_SCALES:
        if s['key'] == scale_key:
            scale_info = s
            break
    if not scale_info:
        return jsonify({'error': f'Invalid scale: {scale_key}'}), 400

    try:
        # Get chart metadata from VSP API
        resp = http_requests.get(
            'https://app.aavso.org/vsp/api/chart/',
            params={'format': 'json', 'star': star_name, 'fov': scale_info['fov'], 'maglimit': 14.5},
            timeout=15
        )
        if resp.status_code != 200:
            return jsonify({'error': f'VSP API error: HTTP {resp.status_code}'}), 502

        data = resp.json()
        chartid = data.get('chartid', '')
        image_url = data.get('image_uri', '').replace('?format=json', '')

        if not image_url:
            return jsonify({'error': 'No image URL from VSP'}), 502

        # Download the image
        img_resp = http_requests.get(image_url, timeout=30)
        if img_resp.status_code != 200:
            return jsonify({'error': f'Image download failed: HTTP {img_resp.status_code}'}), 502

        # Save locally
        safe = _safe_dirname(star_name)
        star_dir = os.path.join(CHARTS_DIR, safe)
        os.makedirs(star_dir, exist_ok=True)

        png_path = os.path.join(star_dir, f"{scale_key}.png")
        with open(png_path, 'wb') as f:
            f.write(img_resp.content)

        # Save metadata
        meta_path = os.path.join(star_dir, f"{scale_key}.meta")
        with open(meta_path, 'w') as f:
            f.write(chartid)

        return jsonify({
            'success': True,
            'scale': scale_key,
            'chartid': chartid,
            'image_url': f"/static/charts/{safe}/{scale_key}.png",
            'size': len(img_resp.content),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@web.route('/vsp/download-all', methods=['POST'])
@login_required
def vsp_download_all_charts():
    """Download all chart scales for a star"""
    star_name = request.form.get('star_name', '').strip()
    if not star_name:
        return jsonify({'error': 'Missing star_name'}), 400

    results = []
    for s in VSP_SCALES:
        try:
            resp = http_requests.get(
                'https://app.aavso.org/vsp/api/chart/',
                params={'format': 'json', 'star': star_name, 'fov': s['fov'], 'maglimit': 14.5},
                timeout=15
            )
            if resp.status_code != 200:
                results.append({'scale': s['key'], 'error': f'API HTTP {resp.status_code}'})
                continue

            data = resp.json()
            chartid = data.get('chartid', '')
            image_url = data.get('image_uri', '').replace('?format=json', '')
            if not image_url:
                results.append({'scale': s['key'], 'error': 'No image URL'})
                continue

            img_resp = http_requests.get(image_url, timeout=30)
            if img_resp.status_code != 200:
                results.append({'scale': s['key'], 'error': f'Image HTTP {img_resp.status_code}'})
                continue

            safe = _safe_dirname(star_name)
            star_dir = os.path.join(CHARTS_DIR, safe)
            os.makedirs(star_dir, exist_ok=True)

            with open(os.path.join(star_dir, f"{s['key']}.png"), 'wb') as f:
                f.write(img_resp.content)
            with open(os.path.join(star_dir, f"{s['key']}.meta"), 'w') as f:
                f.write(chartid)

            results.append({
                'scale': s['key'],
                'success': True,
                'chartid': chartid,
                'image_url': f"/static/charts/{safe}/{s['key']}.png",
            })
        except Exception as e:
            results.append({'scale': s['key'], 'error': str(e)})

    return jsonify({'star': star_name, 'results': results})

@web.route('/vsp/view/<path:star_name>')
@login_required
def vsp_view(star_name):
    """View all AAVSO VSP charts for a variable star"""
    local_charts = _get_local_charts(star_name)
    downloaded_scales = [c['scale'] for c in local_charts]
    scales = []
    for s in VSP_SCALES:
        entry = dict(s)
        entry['downloaded'] = s['key'] in downloaded_scales
        scales.append(entry)
    return render_template('vsx/charts.html', star_name=star_name, scales=scales, local_charts=local_charts)

# ============================================================================
# COMET IMPORT
# ============================================================================

@web.route('/comets/import', methods=['GET', 'POST'])
@login_required
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

# ============================================================================
# VSX VARIABLE STAR IMPORT
# ============================================================================

@web.route('/vsx/import', methods=['GET', 'POST'])
@login_required
def import_vsx():
    """Search and import variable stars from AAVSO VSX"""
    if request.method == 'POST':
        try:
            action = request.form.get('action')
            name = request.form.get('name', '').strip() or None
            constellation = request.form.get('constellation', '').strip() or None
            var_type = request.form.get('var_type', '').strip() or None
            max_records = request.form.get('max_records', '100')

            try:
                max_records = int(max_records)
                max_records = max(1, min(max_records, 9999))
            except:
                max_records = 100

            if action == 'import':
                stats = import_vsx_stars(
                    name=name, constellation=constellation,
                    var_type=var_type, max_records=max_records,
                    update_existing=False
                )
                if 'error' in stats:
                    flash(f"Error: {stats['error']}", 'danger')
                else:
                    flash(
                        f"Import complete! Found {stats.get('total_found', 0)}, "
                        f"added {stats.get('added', 0)}, "
                        f"skipped {stats.get('skipped', 0)}",
                        'success'
                    )
            elif action == 'sync':
                stats = sync_vsx_stars(
                    name=name, constellation=constellation,
                    var_type=var_type, max_records=max_records
                )
                if 'error' in stats:
                    flash(f"Error: {stats['error']}", 'danger')
                else:
                    flash(
                        f"Sync complete! Found {stats.get('total_found', 0)}, "
                        f"added {stats.get('added', 0)}, "
                        f"updated {stats.get('updated', 0)}",
                        'success'
                    )

            return redirect(url_for('web.list_objects'))
        except Exception as e:
            flash(f'Error importing from VSX: {str(e)}', 'danger')

    # Get current variable star count
    try:
        var_star_type = Type.query.filter_by(name='Variable Star').first()
        if var_star_type:
            var_star_count = Object.query.filter_by(type=var_star_type.id).count()
        else:
            var_star_count = 0
    except:
        var_star_count = 0

    return render_template('vsx/import.html', var_star_count=var_star_count)

# ============================================================================
# SIMBAD SEARCH & IMPORT
# ============================================================================

@web.route('/simbad/search', methods=['GET', 'POST'])
@login_required
def search_simbad_page():
    """Search SIMBAD and import objects"""
    results = None
    query_text = ''
    search_type = 'name'
    max_records = 50
    import_message = None

    if request.method == 'POST':
        action = request.form.get('action', 'search')

        if action == 'import_one':
            # Import a single object from search results
            import_name = request.form.get('import_name', '').strip()
            if import_name:
                try:
                    obj_data = lookup_simbad_object(import_name)
                    if obj_data:
                        result = import_simbad_object(obj_data)
                        if result['status'] == 'added':
                            flash(f"Added {result['name']} as {result.get('type', 'object')} (ID: {result['id']})", 'success')
                        elif result['status'] == 'exists':
                            flash(f"{result['name']} already exists in database (ID: {result['id']})", 'warning')
                    else:
                        flash(f"Could not find '{import_name}' in SIMBAD", 'danger')
                except Exception as e:
                    flash(f"Error importing: {str(e)}", 'danger')

            # Restore previous search
            query_text = request.form.get('query', '').strip()
            search_type = request.form.get('search_type', 'name')
            max_records = int(request.form.get('max_records', '50') or '50')
            if query_text:
                try:
                    results = search_simbad(query_text, search_type=search_type, max_records=max_records)
                except:
                    results = []

        elif action == 'import_all':
            # Import all results from search
            query_text = request.form.get('query', '').strip()
            search_type = request.form.get('search_type', 'name')
            max_records = int(request.form.get('max_records', '50') or '50')
            if query_text:
                try:
                    results = search_simbad(query_text, search_type=search_type, max_records=max_records)
                    if results:
                        added = 0
                        skipped = 0
                        for obj_data in results:
                            try:
                                r = import_simbad_object(obj_data)
                                if r['status'] == 'added':
                                    added += 1
                                else:
                                    skipped += 1
                            except:
                                skipped += 1
                        flash(f"Imported {added} objects, {skipped} skipped/already exist", 'success')
                except Exception as e:
                    flash(f"Error: {str(e)}", 'danger')
                    results = []

        else:
            # Regular search
            query_text = request.form.get('query', '').strip()
            search_type = request.form.get('search_type', 'name')
            max_records = int(request.form.get('max_records', '50') or '50')
            if query_text:
                try:
                    results = search_simbad(query_text, search_type=search_type, max_records=max_records)
                    if not results:
                        flash(f"No results found for '{query_text}'", 'warning')
                except Exception as e:
                    flash(f"SIMBAD query error: {str(e)}", 'danger')
                    results = []
            else:
                flash("Please enter a search query", 'warning')

    # Get current object count
    try:
        obj_count = Object.query.count()
    except:
        obj_count = 0

    return render_template('simbad/search.html',
                          results=results,
                          query=query_text,
                          search_type=search_type,
                          max_records=max_records,
                          obj_count=obj_count)

@web.route('/simbad/api/search')
@login_required
def simbad_api_search():
    """AJAX endpoint for SIMBAD quick search"""
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify([])

    try:
        results = search_simbad(query, search_type='name', max_records=10)
        return jsonify(results or [])
    except:
        return jsonify([])
'''
    
    with open('web_routes.py', 'w') as f:
        f.write(content)
    
    print("Created new web_routes.py with proper ID handling!")
    return True

if __name__ == '__main__':
    create_new_web_routes()