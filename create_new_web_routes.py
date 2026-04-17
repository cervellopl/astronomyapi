"""
Create a complete new web_routes.py with proper ID handling
"""

def create_new_web_routes():
    """Create a complete new web_routes.py"""
    print("Creating new web_routes.py...")
    
    content = '''"""
Web interface routes for Astronomy Observations
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_login import login_user, logout_user, login_required, current_user
from models import Type, Property, Place, Instrument, Object, Observation, Session, User
from database import db
from datetime import datetime
from sqlalchemy import func
import json
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
                current_user.cobs_username = request.form.get('cobs_username', '').strip() or None
                cobs_pw = request.form.get('cobs_password', '').strip()
                if cobs_pw:
                    current_user.cobs_password = cobs_pw
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

@web.route('/objects/<int:object_id>')
@login_required
def view_object(object_id):
    """View object details"""
    try:
        obj = Object.query.get(object_id)
        if not obj:
            flash('Object not found', 'danger')
            return redirect(url_for('web.list_objects'))

        # Parse props JSON
        props = {}
        if obj.props:
            try:
                import json
                props = json.loads(obj.props)
            except:
                props = {'raw': obj.props}

        # Get type name
        obj_type = Type.query.get(obj.type) if obj.type else None

        return render_template('objects/view.html', obj=obj, props=props, obj_type=obj_type)
    except Exception as e:
        flash(f'Error loading object: {str(e)}', 'danger')
        return redirect(url_for('web.list_objects'))

@web.route('/objects/<int:object_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_object(object_id):
    """Edit an existing object"""
    obj = Object.query.get(object_id)
    if not obj:
        flash('Object not found', 'danger')
        return redirect(url_for('web.list_objects'))

    if request.method == 'POST':
        try:
            obj.name = request.form.get('name')
            obj.desination = request.form.get('desination')
            obj.type = int(request.form.get('type'))

            # Handle properties - merge individual fields with JSON
            import json
            props = {}
            if obj.props:
                try:
                    props = json.loads(obj.props)
                except:
                    props = {}

            # Update individual property fields
            ra_2000 = request.form.get('ra_2000', '').strip()
            dec_2000 = request.form.get('dec_2000', '').strip()
            constellation = request.form.get('constellation', '').strip()
            magnitude_v = request.form.get('magnitude_v', '').strip()
            spectral_type = request.form.get('spectral_type', '').strip()
            variability_type = request.form.get('variability_type', '').strip()
            period_days = request.form.get('period_days', '').strip()
            max_magnitude = request.form.get('max_magnitude', '').strip()
            min_magnitude = request.form.get('min_magnitude', '').strip()

            if ra_2000:
                props['ra_2000'] = ra_2000
            elif 'ra_2000' in props:
                del props['ra_2000']

            if dec_2000:
                props['dec_2000'] = dec_2000
            elif 'dec_2000' in props:
                del props['dec_2000']

            if constellation:
                props['constellation'] = constellation
            elif 'constellation' in props:
                del props['constellation']

            if magnitude_v:
                props['magnitude_v'] = magnitude_v
            elif 'magnitude_v' in props:
                del props['magnitude_v']

            if spectral_type:
                props['spectral_type'] = spectral_type
            elif 'spectral_type' in props:
                del props['spectral_type']

            if variability_type:
                props['variability_type'] = variability_type
            elif 'variability_type' in props:
                del props['variability_type']

            if period_days:
                props['period_days'] = period_days
            elif 'period_days' in props:
                del props['period_days']

            if max_magnitude:
                props['max_magnitude'] = max_magnitude
            elif 'max_magnitude' in props:
                del props['max_magnitude']

            if min_magnitude:
                props['min_magnitude'] = min_magnitude
            elif 'min_magnitude' in props:
                del props['min_magnitude']

            # Also allow raw JSON override
            extra_props_json = request.form.get('extra_props', '').strip()
            if extra_props_json:
                try:
                    extra = json.loads(extra_props_json)
                    props.update(extra)
                except:
                    pass

            obj.props = json.dumps(props) if props else None

            db.session.commit()
            flash(f'Object "{obj.name}" updated successfully!', 'success')
            return redirect(url_for('web.view_object', object_id=obj.id))
        except Exception as e:
            flash(f'Error updating object: {str(e)}', 'danger')
            db.session.rollback()

    # Parse current props
    import json
    props = {}
    if obj.props:
        try:
            props = json.loads(obj.props)
        except:
            props = {}

    types = Type.query.all()
    return render_template('objects/edit.html', obj=obj, types=types, props=props)

@web.route('/objects/<int:object_id>/delete', methods=['POST'])
@login_required
def delete_object(object_id):
    """Delete an object"""
    try:
        obj = Object.query.get(object_id)
        if not obj:
            flash('Object not found', 'danger')
            return redirect(url_for('web.list_objects'))

        name = obj.name
        db.session.delete(obj)
        db.session.commit()
        flash(f'Object "{name}" deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting object: {str(e)}', 'danger')
        db.session.rollback()

    return redirect(url_for('web.list_objects'))

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

    # Build session metadata for auto-fill
    import json as _json
    session_meta = {}
    for s in sessions:
        meta = {
            'instrument': s.instrument,
            'start_datetime': s.start_datetime.strftime('%Y-%m-%dT%H:%M:%S') if s.start_datetime else '',
            'limiting_magnitude': s.limiting_magnitude,
        }
        # Find place from most recent observation in this session
        last_obs = Observation.query.filter_by(session_id=s.id).order_by(Observation.datetime.desc()).first()
        meta['place'] = last_obs.place if last_obs else None
        session_meta[s.id] = meta

    return render_template('observations/add.html',
                         objects=objects,
                         places=places,
                         instruments=instruments,
                         properties=properties,
                         sessions=sessions,
                         session_meta_json=_json.dumps(session_meta))

@web.route('/observations/<int:obs_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_observation(obs_id):
    """Edit an existing observation"""
    obs = Observation.query.get(obs_id)
    if not obs:
        flash('Observation not found', 'danger')
        return redirect(url_for('web.list_observations'))

    if request.method == 'POST':
        try:
            obs.object = int(request.form.get('object'))
            obs.place = int(request.form.get('place'))
            obs.instrument = int(request.form.get('instrument'))
            session_id = request.form.get('session')
            obs.session_id = int(session_id) if session_id else None
            datetime_str = request.form.get('datetime')
            if datetime_str:
                obs.datetime = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            obs.observation = request.form.get('observation')

            prop1 = request.form.get('prop1')
            prop1value = request.form.get('prop1value')
            if prop1 and prop1value:
                obs.prop1 = int(prop1)
                obs.prop1value = prop1value
            else:
                obs.prop1 = None
                obs.prop1value = None

            db.session.commit()
            flash('Observation updated successfully!', 'success')
            return redirect(url_for('web.list_observations'))
        except Exception as e:
            flash(f'Error updating observation: {str(e)}', 'danger')
            db.session.rollback()

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

    return render_template('observations/edit.html', obs=obs,
                         objects=objects, places=places,
                         instruments=instruments, properties=properties,
                         sessions=sessions)

@web.route('/observations/<int:obs_id>/delete', methods=['POST'])
@login_required
def delete_observation(obs_id):
    """Delete an observation"""
    try:
        obs = Observation.query.get(obs_id)
        if not obs:
            flash('Observation not found', 'danger')
            return redirect(url_for('web.list_observations'))
        db.session.delete(obs)
        db.session.commit()
        flash('Observation deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting observation: {str(e)}', 'danger')
        db.session.rollback()
    return redirect(url_for('web.list_observations'))

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

@web.route('/instruments/<int:inst_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_instrument(inst_id):
    """Edit an existing instrument"""
    inst = Instrument.query.get(inst_id)
    if not inst:
        flash('Instrument not found', 'danger')
        return redirect(url_for('web.list_instruments'))

    if request.method == 'POST':
        try:
            inst.name = request.form.get('name')
            inst.instrument_type = request.form.get('instrument_type') or None
            inst.aperture = request.form.get('aperture') or None
            inst.power = request.form.get('power') or None
            inst.eyepiece = request.form.get('eyepiece') or None

            db.session.commit()
            flash(f'Instrument "{inst.name}" updated successfully!', 'success')
            return redirect(url_for('web.list_instruments'))
        except Exception as e:
            flash(f'Error updating instrument: {str(e)}', 'danger')
            db.session.rollback()

    return render_template('instruments/edit.html', inst=inst)

@web.route('/instruments/<int:inst_id>/delete', methods=['POST'])
@login_required
def delete_instrument(inst_id):
    """Delete an instrument"""
    try:
        inst = Instrument.query.get(inst_id)
        if not inst:
            flash('Instrument not found', 'danger')
            return redirect(url_for('web.list_instruments'))
        name = inst.name
        db.session.delete(inst)
        db.session.commit()
        flash(f'Instrument "{name}" deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting instrument: {str(e)}', 'danger')
        db.session.rollback()
    return redirect(url_for('web.list_instruments'))

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
            alias = request.form.get('alias')
            lat = request.form.get('lat')
            lon = request.form.get('lon')
            alt = request.form.get('alt')
            timezone = request.form.get('timezone')

            # Create new place (id is AUTO_INCREMENT)
            new_place = Place(
                name=name,
                alias=alias if alias else None,
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

@web.route('/places/<int:place_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_place(place_id):
    """Edit an existing place"""
    place = Place.query.get(place_id)
    if not place:
        flash('Place not found', 'danger')
        return redirect(url_for('web.list_places'))

    if request.method == 'POST':
        try:
            place.name = request.form.get('name')
            place.alias = request.form.get('alias') or None
            place.lat = request.form.get('lat')
            place.lon = request.form.get('lon')
            place.alt = request.form.get('alt') or None
            place.timezone = request.form.get('timezone') or None

            db.session.commit()
            flash(f'Place "{place.name}" updated successfully!', 'success')
            return redirect(url_for('web.list_places'))
        except Exception as e:
            flash(f'Error updating place: {str(e)}', 'danger')
            db.session.rollback()

    return render_template('places/edit.html', place=place)

@web.route('/places/<int:place_id>/delete', methods=['POST'])
@login_required
def delete_place(place_id):
    """Delete a place"""
    try:
        place = Place.query.get(place_id)
        if not place:
            flash('Place not found', 'danger')
            return redirect(url_for('web.list_places'))
        name = place.name
        db.session.delete(place)
        db.session.commit()
        flash(f'Place "{name}" deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting place: {str(e)}', 'danger')
        db.session.rollback()
    return redirect(url_for('web.list_places'))

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

@web.route('/types/<int:type_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_type(type_id):
    """Edit an existing type"""
    type_obj = Type.query.get(type_id)
    if not type_obj:
        flash('Type not found', 'danger')
        return redirect(url_for('web.list_types'))

    if request.method == 'POST':
        try:
            type_obj.name = request.form.get('name')
            db.session.commit()
            flash(f'Type "{type_obj.name}" updated successfully!', 'success')
            return redirect(url_for('web.list_types'))
        except Exception as e:
            flash(f'Error updating type: {str(e)}', 'danger')
            db.session.rollback()

    return render_template('types/edit.html', type_obj=type_obj)

@web.route('/types/<int:type_id>/delete', methods=['POST'])
@login_required
def delete_type(type_id):
    """Delete a type"""
    try:
        type_obj = Type.query.get(type_id)
        if not type_obj:
            flash('Type not found', 'danger')
            return redirect(url_for('web.list_types'))
        name = type_obj.name
        db.session.delete(type_obj)
        db.session.commit()
        flash(f'Type "{name}" deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting type: {str(e)}', 'danger')
        db.session.rollback()
    return redirect(url_for('web.list_types'))

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

@web.route('/properties/<int:prop_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_property(prop_id):
    """Edit an existing property"""
    prop = Property.query.get(prop_id)
    if not prop:
        flash('Property not found', 'danger')
        return redirect(url_for('web.list_properties'))

    if request.method == 'POST':
        try:
            prop.name = request.form.get('name')
            prop.valueType = request.form.get('valueType')
            db.session.commit()
            flash(f'Property "{prop.name}" updated successfully!', 'success')
            return redirect(url_for('web.list_properties'))
        except Exception as e:
            flash(f'Error updating property: {str(e)}', 'danger')
            db.session.rollback()

    return render_template('properties/edit.html', prop=prop)

@web.route('/properties/<int:prop_id>/delete', methods=['POST'])
@login_required
def delete_property(prop_id):
    """Delete a property"""
    try:
        prop = Property.query.get(prop_id)
        if not prop:
            flash('Property not found', 'danger')
            return redirect(url_for('web.list_properties'))
        name = prop.name
        db.session.delete(prop)
        db.session.commit()
        flash(f'Property "{name}" deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting property: {str(e)}', 'danger')
        db.session.rollback()
    return redirect(url_for('web.list_properties'))

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

@web.route('/sessions/<int:session_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_session(session_id):
    """Edit an existing session"""
    sess = Session.query.get(session_id)
    if not sess:
        flash('Session not found', 'danger')
        return redirect(url_for('web.list_sessions'))

    if request.method == 'POST':
        try:
            sess.number = request.form.get('number')
            start_str = request.form.get('start_datetime')
            end_str = request.form.get('end_datetime')
            sess.start_datetime = datetime.fromisoformat(start_str.replace('Z', '+00:00')) if start_str else None
            sess.end_datetime = datetime.fromisoformat(end_str.replace('Z', '+00:00')) if end_str else None
            cloud_pct = request.form.get('cloud_percentage')
            sess.cloud_percentage = int(cloud_pct) if cloud_pct else None
            sess.cloud_type = request.form.get('cloud_type') or None
            lp = request.form.get('light_pollution')
            sess.light_pollution = int(lp) if lp else None
            lm = request.form.get('limiting_magnitude')
            sess.limiting_magnitude = float(lm) if lm else None
            sess.moon_phase = request.form.get('moon_phase') or None
            ma = request.form.get('moon_altitude')
            sess.moon_altitude = float(ma) if ma else None
            inst = request.form.get('instrument')
            sess.instrument = int(inst) if inst else None

            db.session.commit()
            flash(f'Session "{sess.number}" updated successfully!', 'success')
            return redirect(url_for('web.view_session', session_id=sess.id))
        except Exception as e:
            flash(f'Error updating session: {str(e)}', 'danger')
            db.session.rollback()

    try:
        instruments = Instrument.query.all()
    except:
        instruments = []

    return render_template('sessions/edit.html', sess=sess, instruments=instruments)

@web.route('/sessions/<int:session_id>/delete', methods=['POST'])
@login_required
def delete_session(session_id):
    """Delete a session"""
    try:
        sess = Session.query.get(session_id)
        if not sess:
            flash('Session not found', 'danger')
            return redirect(url_for('web.list_sessions'))
        number = sess.number
        db.session.delete(sess)
        db.session.commit()
        flash(f'Session "{number}" deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting session: {str(e)}', 'danger')
        db.session.rollback()
    return redirect(url_for('web.list_sessions'))

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


# ============================================================================
# ICQ FORMAT EXPORT
# ============================================================================

import re as _re

def _parse_cobs_data(observation_text):
    """Parse COBS data block from observation text field.
    Returns dict with keys: m1, Coma, DC, Tail, PA, Ref, Sky, Method
    """
    result = {}
    if not observation_text:
        return result
    match = _re.search(r'\\[COBS:\\s*(.+?)\\]', observation_text)
    if not match:
        return result
    for part in match.group(1).split(','):
        part = part.strip()
        if ':' in part:
            key, val = part.split(':', 1)
            result[key.strip()] = val.strip()
    return result


def _parse_comet_designation(designation):
    """Parse comet designation into ICQ columns 1-11.
    Returns (sp_number, year, halfmonth_letter, halfmonth_num, component).
    Examples: '1P/Halley' -> ('  1', '', '', '', '  ')
              'C/2020 F3' -> ('   ', '2020', 'F', '3', '  ')
              '29P/Schwassmann-Wachmann' -> (' 29', '', '', '', '  ')
    """
    sp_number = '   '
    year = '    '
    halfmonth_letter = ' '
    halfmonth_num = ' '
    component = '  '

    if not designation:
        return sp_number, year, halfmonth_letter, halfmonth_num, component

    designation = designation.strip()

    # Periodic comet: "1P/...", "29P/..."
    m = _re.match(r'^(\\d+)[PpDd]/', designation)
    if m:
        num = m.group(1)
        sp_number = num.rjust(3)[:3]
        return sp_number, year, halfmonth_letter, halfmonth_num, component

    # Non-periodic: "C/2020 F3", "C/2024 A1b"
    m = _re.match(r'^[CPDXAI]/(\\d{4})\\s+([A-Z])(\\d+)([a-z])?', designation)
    if m:
        year = m.group(1)
        halfmonth_letter = m.group(2)
        halfmonth_num = m.group(3)[0] if m.group(3) else ' '
        comp = m.group(4) if m.group(4) else '  '
        if len(comp) == 1:
            comp = comp + ' '
        component = comp[:2]
        return sp_number, year, halfmonth_letter, halfmonth_num, component

    return sp_number, year, halfmonth_letter, halfmonth_num, component


def _format_icq_magnitude(mag_str):
    """Format magnitude for ICQ columns 28-33.
    Format: ' mm.m ' with decimal in column 31 (position 4 within field).
    """
    if not mag_str:
        return '      '
    try:
        mag = float(mag_str)
        # Format as right-justified with one decimal: ' mm.m '
        formatted = f'{mag:5.1f}'
        return formatted + ' '
    except (ValueError, TypeError):
        return '      '


def _format_icq_aperture(aperture_str):
    """Format instrument aperture for ICQ columns 36-40.
    Should be in cm, significant figures only.
    """
    if not aperture_str:
        return '     '
    try:
        ap = float(aperture_str)
        if ap == int(ap):
            formatted = f'{int(ap):>5}'
        else:
            formatted = f'{ap:5.1f}'
        return formatted[:5]
    except (ValueError, TypeError):
        # Try to extract number
        m = _re.search(r'([\\d.]+)', str(aperture_str))
        if m:
            return _format_icq_aperture(m.group(1))
        return '     '


def _format_icq_coma(coma_str):
    """Format coma diameter for ICQ columns 49-54.
    In arcminutes, significant figures.
    """
    if not coma_str:
        return '      '
    # Strip unit suffixes like ' or arcmin
    cleaned = _re.sub(r"['\\"arcmin\\s]", '', str(coma_str))
    try:
        coma = float(cleaned)
        if coma >= 100:
            formatted = f'{coma:6.1f}'
        elif coma >= 10:
            formatted = f'{coma:6.2f}'
        else:
            formatted = f'{coma:6.2f}'
        return formatted[:6]
    except (ValueError, TypeError):
        return '      '


def _format_icq_tail(tail_str):
    """Format tail length for ICQ columns 59-64.
    In degrees, or with 'm' suffix for arcminutes.
    """
    if not tail_str:
        return '      '
    cleaned = str(tail_str).strip()
    # Check for degree symbol or 'd'
    is_arcmin = "'" in cleaned or 'arcmin' in cleaned.lower() or 'm' in cleaned.lower()
    cleaned = _re.sub(r"[°'\\"darcmin\\s]", '', cleaned)
    try:
        val = float(cleaned)
        if is_arcmin:
            formatted = f'{val:5.1f}m'
        else:
            formatted = f'{val:5.2f} '
        return formatted[:6]
    except (ValueError, TypeError):
        return '      '


def _format_icq_line(obs, obj, instrument, place, observer_code):
    """Format a single observation into an 80-character ICQ line."""
    cobs = _parse_cobs_data(obs.observation)
    if not cobs:
        return None  # Skip non-comet observations

    # Columns 1-11: Comet designation
    sp, yr, hl, hn, comp = _parse_comet_designation(obj.desination if obj else '')

    # Columns 12-23: Date of observation
    dt = obs.datetime
    if not dt:
        return None
    obs_year = f'{dt.year:4d}'
    obs_month = f'{dt.month:02d}'
    day_frac = dt.day + dt.hour / 24.0 + dt.minute / 1440.0
    obs_day = f'{day_frac:06.2f}'  # DD.DD with leading zero

    # Column 24-25: spaces
    # Column 26: extinction notes (blank)
    # Column 27: magnitude method
    method = cobs.get('Method', '').upper()
    if method == 'CCD':
        mag_method = 'Z'
    elif method == 'VISUAL':
        mag_method = 'B'  # Bobrovnikoff method (default for visual)
    else:
        mag_method = ' '

    # Columns 28-33: magnitude
    magnitude = _format_icq_magnitude(cobs.get('m1'))

    # Columns 34-35: reference stars catalog
    ref = cobs.get('Ref', '')[:2].ljust(2)

    # Columns 36-40: aperture (cm)
    aperture = _format_icq_aperture(instrument.aperture if instrument else '')

    # Column 41: instrument type
    inst_type = ' '
    if instrument and instrument.instrument_type:
        itype = instrument.instrument_type.upper()
        if 'REFRACT' in itype:
            inst_type = 'R'
        elif 'REFLECT' in itype or 'NEWT' in itype:
            inst_type = 'N'
        elif 'CASSEGRAIN' in itype or 'SCT' in itype or 'SCHMIDT' in itype:
            inst_type = 'S'
        elif 'BINOC' in itype:
            inst_type = 'B'
        elif 'NAKED' in itype or 'EYE' in itype:
            inst_type = 'E'
        elif 'CCD' in itype or 'CAMERA' in itype:
            inst_type = 'L'
        else:
            inst_type = 'L'

    # Columns 42-43: focal ratio
    focal_ratio = '  '

    # Columns 44-47: power/magnification
    power = '    '
    if instrument and instrument.power:
        try:
            p = int(float(instrument.power))
            power = f'{p:>4}'[:4]
        except (ValueError, TypeError):
            pass

    # Column 48: space
    # Columns 49-54: coma diameter
    coma = _format_icq_coma(cobs.get('Coma'))

    # Column 55: central condensation appearance (blank)
    cond_appearance = ' '

    # Columns 56-57: degree of condensation
    dc = cobs.get('DC', '')
    if dc:
        try:
            dc_val = int(float(dc))
            dc_str = f'{dc_val:>1} '
        except (ValueError, TypeError):
            dc_str = '  '
    else:
        dc_str = '  '

    # Column 58: space
    # Columns 59-64: tail length
    tail = _format_icq_tail(cobs.get('Tail'))

    # Columns 65-67: position angle
    pa = cobs.get('PA', '')
    if pa:
        try:
            pa_val = int(float(pa))
            pa_str = f'{pa_val:>3}'[:3]
        except (ValueError, TypeError):
            pa_str = '   '
    else:
        pa_str = '   '

    # Column 68: space
    # Columns 69-74: publication reference (blank)
    pub_ref = '      '

    # Column 75: revision indicator
    revision = ' '

    # Columns 76-80: observer code
    obs_code = (observer_code or '').ljust(5)[:5]

    # Assemble the 80-character line
    line = (
        f'{sp}'               # 1-3
        f'{yr}'               # 4-7
        f'{hl}'               # 8
        f'{hn}'               # 9
        f'{comp}'             # 10-11
        f'{obs_year}'         # 12-15
        f'{obs_month}'        # 16-17
        f'{obs_day}'          # 18-23
        f'  '                 # 24-25
        f' '                  # 26
        f'{mag_method}'       # 27
        f'{magnitude}'        # 28-33
        f'{ref}'              # 34-35
        f'{aperture}'         # 36-40
        f'{inst_type}'        # 41
        f'{focal_ratio}'      # 42-43
        f'{power}'            # 44-47
        f' '                  # 48
        f'{coma}'             # 49-54
        f'{cond_appearance}'  # 55
        f'{dc_str}'           # 56-57
        f' '                  # 58
        f'{tail}'             # 59-64
        f'{pa_str}'           # 65-67
        f' '                  # 68
        f'{pub_ref}'          # 69-74
        f'{revision}'         # 75
        f'{obs_code}'         # 76-80
    )

    return line[:80]


@web.route('/export/icq', methods=['GET', 'POST'])
@login_required
def export_icq():
    """Export comet observations in ICQ format."""
    comet_observations = []
    icq_lines = []
    exported = False

    try:
        # Get comet type
        comet_type = Type.query.filter_by(name='Comet').first()

        # Get all comet objects
        comet_objects = []
        if comet_type:
            comet_objects = Object.query.filter_by(type=comet_type.id).all()
        comet_ids = [c.id for c in comet_objects]
        comet_lookup = {c.id: c for c in comet_objects}

        # Get all instruments lookup
        instruments = {i.id: i for i in Instrument.query.all()}

        # Get all places lookup
        places = {p.id: p for p in Place.query.all()}

        # Get observer code from current user
        observer_code = current_user.icq_code or ''

        if request.method == 'POST':
            exported = True
            # Filter parameters
            comet_id = request.form.get('comet_id')
            date_from = request.form.get('date_from')
            date_to = request.form.get('date_to')

            # Build query
            query = Observation.query.filter(Observation.object.in_(comet_ids))

            if comet_id and comet_id != 'all':
                query = query.filter(Observation.object == int(comet_id))
            if date_from:
                query = query.filter(Observation.datetime >= datetime.fromisoformat(date_from))
            if date_to:
                query = query.filter(Observation.datetime <= datetime.fromisoformat(date_to + 'T23:59:59'))

            query = query.order_by(Observation.datetime)
            comet_observations = query.all()

            # Generate ICQ lines
            for obs in comet_observations:
                obj = comet_lookup.get(obs.object)
                inst = instruments.get(obs.instrument)
                line = _format_icq_line(obs, obj, inst, places.get(obs.place), observer_code)
                if line:
                    icq_lines.append({
                        'line': line,
                        'obs_id': obs.id,
                        'comet_name': obj.name if obj else 'Unknown',
                        'date': obs.datetime.strftime('%Y-%m-%d %H:%M') if obs.datetime else '',
                    })

    except Exception as e:
        flash(f'Error loading comet observations: {str(e)}', 'danger')

    return render_template('export/icq.html',
                         comet_objects=comet_objects if 'comet_objects' in dir() else [],
                         icq_lines=icq_lines,
                         total_observations=len(comet_observations),
                         exported=exported)


@web.route('/export/icq/download', methods=['POST'])
@login_required
def export_icq_download():
    """Download comet observations as ICQ format text file."""
    try:
        comet_type = Type.query.filter_by(name='Comet').first()
        comet_objects = Object.query.filter_by(type=comet_type.id).all() if comet_type else []
        comet_ids = [c.id for c in comet_objects]
        comet_lookup = {c.id: c for c in comet_objects}
        instruments = {i.id: i for i in Instrument.query.all()}
        places = {p.id: p for p in Place.query.all()}
        observer_code = current_user.icq_code or ''

        # Filter parameters
        comet_id = request.form.get('comet_id')
        date_from = request.form.get('date_from')
        date_to = request.form.get('date_to')

        query = Observation.query.filter(Observation.object.in_(comet_ids))
        if comet_id and comet_id != 'all':
            query = query.filter(Observation.object == int(comet_id))
        if date_from:
            query = query.filter(Observation.datetime >= datetime.fromisoformat(date_from))
        if date_to:
            query = query.filter(Observation.datetime <= datetime.fromisoformat(date_to + 'T23:59:59'))

        query = query.order_by(Observation.datetime)
        observations = query.all()

        lines = []
        for obs in observations:
            obj = comet_lookup.get(obs.object)
            inst = instruments.get(obs.instrument)
            line = _format_icq_line(obs, obj, inst, places.get(obs.place), observer_code)
            if line:
                lines.append(line)

        content = '\\n'.join(lines) + '\\n' if lines else ''
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f'comet_observations_icq_{timestamp}.txt'

        return Response(
            content,
            mimetype='text/plain',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as e:
        flash(f'Error exporting ICQ data: {str(e)}', 'danger')
        return redirect(url_for('web.export_icq'))


# ============================================================================
# AAVSO VISUAL FORMAT EXPORT
# ============================================================================

def _parse_aavso_data(observation_text):
    """Parse AAVSO data block from observation text field.
    Returns dict with keys: Magnitude, Uncertainty, Comp1, Comp2, Check,
    Chart, Band, Observer, Method
    """
    result = {}
    if not observation_text:
        return result
    match = _re.search(r'\\[AAVSO:\\s*(.+?)\\]', observation_text)
    if not match:
        return result
    for part in match.group(1).split(','):
        part = part.strip()
        if ':' in part:
            key, val = part.split(':', 1)
            result[key.strip()] = val.strip()
    return result


def _datetime_to_jd(dt):
    """Convert a Python datetime to Julian Date."""
    if not dt:
        return None
    # Julian Date formula
    a = (14 - dt.month) // 12
    y = dt.year + 4800 - a
    m = dt.month + 12 * a - 3
    jdn = dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    jd = jdn + (dt.hour - 12) / 24.0 + dt.minute / 1440.0 + dt.second / 86400.0
    return jd


def _build_aavso_visual_file(observations, objects_lookup, observer_code):
    """Build a complete AAVSO Visual Format file string.

    AAVSO Visual File Format:
    Header:
        #TYPE=Visual
        #OBSCODE=<observer_code>
        #SOFTWARE=Astronomy Observations App
        #DELIM=,
        #DATE=JD
        #OBSTYPE=Visual
    Data (one per line, comma-separated):
        NAME,DATE,MAG,COMMENTCODE,COMP1,COMP2,CHART,NOTES
    """
    lines = []
    # Header
    lines.append('#TYPE=Visual')
    lines.append(f'#OBSCODE={observer_code or "na"}')
    lines.append('#SOFTWARE=Astronomy Observations App')
    lines.append('#DELIM=,')
    lines.append('#DATE=JD')
    lines.append('#OBSTYPE=Visual')

    for obs in observations:
        aavso = _parse_aavso_data(obs.observation)
        if not aavso:
            continue

        obj = objects_lookup.get(obs.object)
        # NAME: star name or designation
        name = ''
        if obj:
            name = obj.desination or obj.name or ''
        name = name.strip() or 'na'

        # DATE: Julian Date
        jd = _datetime_to_jd(obs.datetime)
        date_str = f'{jd:.4f}' if jd else 'na'

        # MAG: magnitude, may include < for fainter-than
        mag = aavso.get('Magnitude', 'na')
        if mag:
            mag = mag.strip()
        if not mag:
            mag = 'na'

        # COMMENTCODE: na unless special circumstances
        # B=cloudy, D=poor seeing, I=identification uncertain,
        # K=non-AAVSO chart, U=discrepant, W=uncertain, Y=outburst, Z=magnitude corrected
        comment_code = 'na'

        # COMP1: comparison star 1
        comp1 = aavso.get('Comp1', 'na')
        if not comp1:
            comp1 = 'na'

        # COMP2: comparison star 2
        comp2 = aavso.get('Comp2', 'na')
        if not comp2:
            comp2 = 'na'

        # CHART: chart id
        chart = aavso.get('Chart', 'na')
        if not chart:
            chart = 'na'

        # NOTES: additional notes (strip out the [AAVSO:...] block itself)
        notes_text = obs.observation or ''
        notes_text = _re.sub(r'\\s*\\[AAVSO:.*?\\]', '', notes_text).strip()
        if not notes_text:
            notes_text = 'na'
        # Commas in notes must be removed since comma is our delimiter
        notes_text = notes_text.replace(',', ';')

        line = f'{name},{date_str},{mag},{comment_code},{comp1},{comp2},{chart},{notes_text}'
        lines.append(line)

    return '\\n'.join(lines) + '\\n'


@web.route('/export/aavso', methods=['GET', 'POST'])
@login_required
def export_aavso():
    """Export variable star observations in AAVSO Visual format."""
    vs_observations = []
    aavso_lines = []
    exported = False

    try:
        # Get variable star type
        vs_type = Type.query.filter_by(name='Variable Star').first()

        # Get all variable star objects
        vs_objects = []
        if vs_type:
            vs_objects = Object.query.filter_by(type=vs_type.id).all()
        vs_ids = [v.id for v in vs_objects]
        vs_lookup = {v.id: v for v in vs_objects}

        # Observer code from user settings
        observer_code = current_user.aavso_code or ''

        if request.method == 'POST':
            exported = True
            star_id = request.form.get('star_id')
            date_from = request.form.get('date_from')
            date_to = request.form.get('date_to')

            query = Observation.query.filter(Observation.object.in_(vs_ids))
            if star_id and star_id != 'all':
                query = query.filter(Observation.object == int(star_id))
            if date_from:
                query = query.filter(Observation.datetime >= datetime.fromisoformat(date_from))
            if date_to:
                query = query.filter(Observation.datetime <= datetime.fromisoformat(date_to + 'T23:59:59'))

            query = query.order_by(Observation.datetime)
            vs_observations = query.all()

            # Build preview lines
            for obs in vs_observations:
                aavso = _parse_aavso_data(obs.observation)
                if not aavso:
                    continue
                obj = vs_lookup.get(obs.object)
                jd = _datetime_to_jd(obs.datetime)
                aavso_lines.append({
                    'obs_id': obs.id,
                    'star_name': obj.name if obj else 'Unknown',
                    'designation': obj.desination if obj else '',
                    'date': obs.datetime.strftime('%Y-%m-%d %H:%M') if obs.datetime else '',
                    'jd': f'{jd:.4f}' if jd else '',
                    'magnitude': aavso.get('Magnitude', ''),
                    'comp1': aavso.get('Comp1', ''),
                    'comp2': aavso.get('Comp2', ''),
                    'chart': aavso.get('Chart', ''),
                })

    except Exception as e:
        flash(f'Error loading variable star observations: {str(e)}', 'danger')

    return render_template('export/aavso.html',
                         vs_objects=vs_objects if 'vs_objects' in dir() else [],
                         aavso_lines=aavso_lines,
                         total_observations=len(vs_observations),
                         exported=exported,
                         observer_code=observer_code if 'observer_code' in dir() else '')


@web.route('/export/aavso/download', methods=['POST'])
@login_required
def export_aavso_download():
    """Download variable star observations as AAVSO Visual format text file."""
    try:
        vs_type = Type.query.filter_by(name='Variable Star').first()
        vs_objects = Object.query.filter_by(type=vs_type.id).all() if vs_type else []
        vs_ids = [v.id for v in vs_objects]
        vs_lookup = {v.id: v for v in vs_objects}
        observer_code = current_user.aavso_code or ''

        star_id = request.form.get('star_id')
        date_from = request.form.get('date_from')
        date_to = request.form.get('date_to')

        query = Observation.query.filter(Observation.object.in_(vs_ids))
        if star_id and star_id != 'all':
            query = query.filter(Observation.object == int(star_id))
        if date_from:
            query = query.filter(Observation.datetime >= datetime.fromisoformat(date_from))
        if date_to:
            query = query.filter(Observation.datetime <= datetime.fromisoformat(date_to + 'T23:59:59'))

        query = query.order_by(Observation.datetime)
        observations = query.all()

        content = _build_aavso_visual_file(observations, vs_lookup, observer_code)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f'variable_stars_aavso_{timestamp}.txt'

        return Response(
            content,
            mimetype='text/plain',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as e:
        flash(f'Error exporting AAVSO data: {str(e)}', 'danger')
        return redirect(url_for('web.export_aavso'))


# ============================================================================
# COBS SUBMISSION (cobs.si)
# ============================================================================

def _cobs_login(session, username, password):
    """Login to COBS and return True on success."""
    r = session.get('https://www.cobs.si/accounts/login/', timeout=15)
    csrf_match = _re.search(r'csrfmiddlewaretoken.*?value=["\\'](.*?)["\\'\\s]', r.text)
    if not csrf_match:
        return False, 'Could not get COBS CSRF token'
    csrf = csrf_match.group(1)
    r2 = session.post('https://www.cobs.si/accounts/login/', data={
        'csrfmiddlewaretoken': csrf,
        'username': username,
        'password': password,
    }, headers={'Referer': 'https://www.cobs.si/accounts/login/'}, allow_redirects=True, timeout=15)
    if 'login' in r2.url:
        return False, 'COBS login failed. Check your credentials in Settings.'
    return True, 'OK'


def _cobs_get_form_csrf(session):
    """Get the observation form CSRF token."""
    r = session.get('https://www.cobs.si/obs/form/vis/', timeout=15)
    if 'login' in r.url:
        return None, None
    csrf_match = _re.search(r'csrfmiddlewaretoken.*?value=["\\'](.*?)["\\'\\s]', r.text)
    if not csrf_match:
        return None, None
    return csrf_match.group(1), r.text


def _aperture_mm_to_cm(aperture_str):
    """Convert aperture from mm to cm for COBS submission.
    Parses strings like '70mm', '200.0mm', '70', extracting the number and dividing by 10.
    """
    if not aperture_str:
        return ''
    import re as _re_local
    m = _re_local.search(r'([\\d.]+)', str(aperture_str))
    if not m:
        return aperture_str
    mm_val = float(m.group(1))
    cm_val = mm_val / 10.0
    # Return as clean number: 7.0 -> '7.0', 20.0 -> '20.0'
    if cm_val == int(cm_val):
        return f'{cm_val:.1f}'
    return str(cm_val)


def _map_instrument_type_to_cobs(instrument):
    """Map local instrument type to COBS instrument_type select value."""
    if not instrument or not instrument.instrument_type:
        return ''
    itype = instrument.instrument_type.upper()
    mapping = {
        'REFRACT': '20', 'NEWT': '12', 'REFLECT': '12',
        'CASSEGRAIN': '3', 'SCT': '22', 'SCHMIDT-CASSEGRAIN': '22',
        'MAKSUTOV': '13', 'BINOC': '2', 'NAKED': '5', 'EYE': '5',
        'CAMERA': '1', 'LENS': '1', 'SCHMIDT': '4',
    }
    for key, val in mapping.items():
        if key in itype:
            return val
    return ''


def _map_obs_method_to_cobs(method_str):
    """Map COBS method field from our app to cobs.si obs_method value."""
    if not method_str:
        return ''
    m = method_str.upper().strip()
    if m == 'VISUAL' or m == 'B':
        return '2'   # B - Simple Out-Out method
    elif m == 'CCD':
        return '47'  # Z - CCD Visual equivalent
    return ''


def _submit_obs_to_cobs(session, csrf, obs, obj, instrument, place, cobs_data):
    """Submit a single observation to COBS. Returns (success, message)."""
    # Find comet in COBS by designation — we pass the COBS comet ID if known,
    # otherwise the user must select it in the preview step.
    form_data = {
        'csrfmiddlewaretoken': csrf,
        'comet': cobs_data.get('cobs_comet_id', ''),
        'obs_date': obs.datetime.strftime('%Y-%m-%d %H:%M') if obs.datetime else '',
        'magnitude': cobs_data.get('magnitude', ''),
        'obs_method': cobs_data.get('obs_method', ''),
        'extinction': '',
        'comet_visibility': '',
        'conditions': '',
        'ref_catalog': cobs_data.get('ref_catalog', '144'),
        'instrument_type': cobs_data.get('instrument_type', ''),
        'instrument_aperture': cobs_data.get('aperture', ''),
        'instrument_focal_ratio': '',
        'instrument_power': cobs_data.get('power', ''),
        'coma_diameter': cobs_data.get('coma', ''),
        'coma_dc': cobs_data.get('dc', ''),
        'coma_visibility': '',
        'coma_notes': '',
        'tail_length': cobs_data.get('tail', ''),
        'tail_pa': cobs_data.get('pa', ''),
        'tail_visibility': '',
        'tail_length_unit': cobs_data.get('tail_unit', 'd'),
        'location': cobs_data.get('location', ''),
        'icq_reference': '',
        'icq_revision': 'unknown',
        'obs_sky_quality': '',
        'obs_sky_quality_method': '',
        'reference_star_names': cobs_data.get('ref', ''),
        'obs_comment': cobs_data.get('comment', ''),
    }

    r = session.post('https://www.cobs.si/obs/form/vis/', data=form_data,
                     headers={'Referer': 'https://www.cobs.si/obs/form/vis/'},
                     allow_redirects=True, timeout=15)

    # Success: COBS redirects to /obs/done/<id>/
    if '/obs/done/' in r.url:
        obs_num = _re.search(r'/obs/done/(\d+)/', r.url)
        obs_id_str = obs_num.group(1) if obs_num else ''
        return True, f'Submitted (COBS #{obs_id_str})'

    # Check for form validation errors
    errors = []
    for m in _re.finditer(r'invalid-feedback["\\'\\s][^>]*>.*?<strong>(.*?)</strong>', r.text, _re.DOTALL):
        errors.append(m.group(1).strip())
    if errors:
        return False, '; '.join(errors)

    # Check for Django errorlist
    for m in _re.finditer(r'errorlist[^>]*>(.*?)</ul>', r.text, _re.DOTALL):
        clean = _re.sub(r'<[^>]+>', ' ', m.group(1)).strip()
        if clean:
            return False, clean

    # If still on the form page, something went wrong
    if '/obs/form/' in r.url:
        return False, 'Form submission failed (unknown error)'

    return True, 'Submitted successfully'


@web.route('/cobs/submit', methods=['GET', 'POST'])
@login_required
def cobs_submit():
    """Submit comet observations to COBS."""
    # Check credentials
    if not current_user.cobs_username or not current_user.cobs_password:
        flash('Please set your COBS credentials in Settings first.', 'warning')
        return redirect(url_for('web.user_settings'))

    comet_observations = []
    preview_data = []
    cobs_comets = []
    submitted_results = []
    step = request.form.get('step', 'filter')

    try:
        comet_type = Type.query.filter_by(name='Comet').first()
        comet_objects = Object.query.filter_by(type=comet_type.id).all() if comet_type else []
        comet_ids = [c.id for c in comet_objects]
        comet_lookup = {c.id: c for c in comet_objects}
        instruments = {i.id: i for i in Instrument.query.all()}
        places = {p.id: p for p in Place.query.all()}

        if request.method == 'POST' and step == 'preview':
            # Build query with filters
            comet_id = request.form.get('comet_id')
            date_from = request.form.get('date_from')
            date_to = request.form.get('date_to')

            query = Observation.query.filter(Observation.object.in_(comet_ids))
            if comet_id and comet_id != 'all':
                query = query.filter(Observation.object == int(comet_id))
            if date_from:
                query = query.filter(Observation.datetime >= datetime.fromisoformat(date_from))
            if date_to:
                query = query.filter(Observation.datetime <= datetime.fromisoformat(date_to + 'T23:59:59'))

            comet_observations = query.order_by(Observation.datetime).all()

            # Login to COBS to get comet list
            cobs_session = http_requests.Session()
            ok, msg = _cobs_login(cobs_session, current_user.cobs_username, current_user.cobs_password)
            if not ok:
                flash(msg, 'danger')
            else:
                csrf, form_html = _cobs_get_form_csrf(cobs_session)
                if form_html:
                    # Extract COBS comet options
                    for m in _re.finditer(r'<option value=["\\'](\\d+)["\\'](.*?)>(.*?)</option>', form_html):
                        cobs_comets.append({'id': m.group(1), 'name': m.group(3).strip()})

            # Build preview data
            for obs in comet_observations:
                cobs = _parse_cobs_data(obs.observation)
                if not cobs:
                    continue
                obj = comet_lookup.get(obs.object)
                inst = instruments.get(obs.instrument)
                place = places.get(obs.place)

                # Try to auto-match COBS comet by name and designation
                matched_cobs_id = ''
                if obj:
                    obj_name = (obj.name or '').strip()
                    obj_des = (obj.desination or '').strip()
                    for cc in cobs_comets:
                        cobs_name = cc['name']
                        # Direct match on designation or name
                        if obj_des and (obj_des in cobs_name or cobs_name in obj_des):
                            matched_cobs_id = cc['id']
                            break
                        if obj_name and (obj_name in cobs_name or cobs_name in obj_name):
                            matched_cobs_id = cc['id']
                            break
                        # Match readable designation from name, e.g. 'C/2025 R3 (PANSTARRS)'
                        # against our name 'C/2025 R3 (PANSTARRS)'
                        # Also handle MPC packed format: C/K25R030 -> C/2025 R3
                        name_parts = obj_name.split('(')[0].strip() if obj_name else ''
                        cobs_parts = cobs_name.split('(')[0].strip()
                        if name_parts and cobs_parts and name_parts == cobs_parts:
                            matched_cobs_id = cc['id']
                            break

                preview_data.append({
                    'obs_id': obs.id,
                    'comet_name': obj.name if obj else 'Unknown',
                    'designation': obj.desination if obj else '',
                    'date': obs.datetime.strftime('%Y-%m-%d %H:%M') if obs.datetime else '',
                    'magnitude': cobs.get('m1', ''),
                    'coma': cobs.get('Coma', ''),
                    'dc': cobs.get('DC', ''),
                    'tail': cobs.get('Tail', ''),
                    'pa': cobs.get('PA', ''),
                    'method': cobs.get('Method', ''),
                    'aperture': _aperture_mm_to_cm(inst.aperture) if inst else '',
                    'power': inst.power if inst else '',
                    'instrument_type': _map_instrument_type_to_cobs(inst),
                    'obs_method': _map_obs_method_to_cobs(cobs.get('Method', '')),
                    'location': (place.alias or place.name) if place else '',
                    'ref': cobs.get('Ref', ''),
                    'matched_cobs_id': matched_cobs_id,
                })
            step = 'preview'

        elif request.method == 'POST' and step == 'submit':
            # Actually submit selected observations
            obs_ids = request.form.getlist('obs_ids')
            if not obs_ids:
                flash('No observations selected.', 'warning')
                return redirect(url_for('web.cobs_submit'))

            cobs_session = http_requests.Session()
            ok, msg = _cobs_login(cobs_session, current_user.cobs_username, current_user.cobs_password)
            if not ok:
                flash(msg, 'danger')
                return redirect(url_for('web.cobs_submit'))

            for obs_id in obs_ids:
                obs = Observation.query.get(int(obs_id))
                if not obs:
                    continue
                cobs = _parse_cobs_data(obs.observation)
                if not cobs:
                    continue

                obj = comet_lookup.get(obs.object)
                inst = instruments.get(obs.instrument)
                place = places.get(obs.place)

                # Get fresh CSRF for each submission
                csrf, _ = _cobs_get_form_csrf(cobs_session)
                if not csrf:
                    submitted_results.append({'obs_id': obs_id, 'success': False, 'msg': 'Could not get form'})
                    continue

                cobs_data = {
                    'cobs_comet_id': request.form.get(f'cobs_comet_{obs_id}', ''),
                    'magnitude': cobs.get('m1', ''),
                    'obs_method': _map_obs_method_to_cobs(cobs.get('Method', '')),
                    'instrument_type': _map_instrument_type_to_cobs(inst),
                    'aperture': _aperture_mm_to_cm(inst.aperture) if inst else '',
                    'power': inst.power if inst else '',
                    'coma': cobs.get('Coma', '').replace("'", '').replace('"', '').strip(),
                    'dc': cobs.get('DC', ''),
                    'tail': cobs.get('Tail', '').replace("'", '').replace('"', '').replace('d', '').replace('m', '').strip(),
                    'pa': cobs.get('PA', ''),
                    'tail_unit': 'd',
                    'location': (place.alias or place.name) if place else '',
                    'ref': cobs.get('Ref', ''),
                    'comment': f'Submitted from Astronomy Observations App',
                }

                success, result_msg = _submit_obs_to_cobs(cobs_session, csrf, obs, obj, inst, place, cobs_data)
                comet_name = obj.name if obj else f'Obs #{obs_id}'
                submitted_results.append({
                    'obs_id': obs_id,
                    'comet_name': comet_name,
                    'date': obs.datetime.strftime('%Y-%m-%d') if obs.datetime else '',
                    'success': success,
                    'msg': result_msg,
                })

            successes = sum(1 for r in submitted_results if r['success'])
            failures = len(submitted_results) - successes
            if successes:
                flash(f'Successfully submitted {successes} observation(s) to COBS!', 'success')
            if failures:
                flash(f'{failures} observation(s) failed to submit.', 'danger')
            step = 'results'

    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')

    return render_template('cobs/submit.html',
                         comet_objects=comet_objects if 'comet_objects' in dir() else [],
                         preview_data=preview_data,
                         cobs_comets=cobs_comets,
                         submitted_results=submitted_results,
                         step=step)


# ============================================================================
# BACKUP / EXPORT / IMPORT / RESTORE
# ============================================================================

def _serialize_datetime(dt):
    """Convert datetime to ISO string or None."""
    return dt.isoformat() if dt else None


def _build_backup_data():
    """Collect all user data into a serializable dict."""
    data = {
        'version': 1,
        'exported_at': datetime.utcnow().isoformat(),
        'types': [],
        'properties': [],
        'places': [],
        'instruments': [],
        'objects': [],
        'sessions': [],
        'observations': [],
    }

    for t in Type.query.all():
        data['types'].append({'id': t.id, 'name': t.name})

    for p in Property.query.all():
        data['properties'].append({'id': p.id, 'name': p.name, 'valueType': p.valueType})

    for p in Place.query.all():
        data['places'].append({
            'id': p.id, 'name': p.name, 'alias': p.alias,
            'lat': p.lat, 'lon': p.lon, 'alt': p.alt,
            'timezone': p.timezone,
        })

    for i in Instrument.query.all():
        data['instruments'].append({
            'id': i.id, 'name': i.name,
            'instrument_type': i.instrument_type,
            'aperture': i.aperture, 'power': i.power,
            'eyepiece': i.eyepiece,
        })

    for o in Object.query.all():
        data['objects'].append({
            'id': o.id, 'name': o.name,
            'desination': o.desination, 'type': o.type,
            'props': o.props,
        })

    for s in Session.query.all():
        data['sessions'].append({
            'id': s.id, 'number': s.number,
            'start_datetime': _serialize_datetime(s.start_datetime),
            'end_datetime': _serialize_datetime(s.end_datetime),
            'cloud_percentage': s.cloud_percentage,
            'cloud_type': s.cloud_type,
            'light_pollution': s.light_pollution,
            'limiting_magnitude': s.limiting_magnitude,
            'moon_phase': s.moon_phase,
            'moon_altitude': s.moon_altitude,
            'instrument': s.instrument,
        })

    for obs in Observation.query.all():
        data['observations'].append({
            'id': obs.id, 'object': obs.object,
            'place': obs.place, 'instrument': obs.instrument,
            'session_id': obs.session_id,
            'datetime': _serialize_datetime(obs.datetime),
            'observation': obs.observation,
            'prop1': obs.prop1, 'prop1value': obs.prop1value,
        })

    return data


def _parse_datetime(s):
    """Parse an ISO datetime string, return None on failure."""
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        return None


def _import_backup_data(data, mode='merge'):
    """Import data from a backup dict.

    mode='merge'   - skip records whose id already exists
    mode='restore' - wipe all tables first, then insert everything
    """
    stats = {'added': {}, 'skipped': {}}

    if mode == 'restore':
        Observation.query.delete()
        Session.query.delete()
        Object.query.delete()
        Instrument.query.delete()
        Place.query.delete()
        Property.query.delete()
        Type.query.delete()
        db.session.flush()

    table_configs = [
        ('types', Type, lambda r: Type(id=r['id'], name=r['name'])),
        ('properties', Property, lambda r: Property(id=r['id'], name=r['name'], valueType=r.get('valueType'))),
        ('places', Place, lambda r: Place(
            id=r['id'], name=r['name'], alias=r.get('alias'),
            lat=r.get('lat'), lon=r.get('lon'), alt=r.get('alt'),
            timezone=r.get('timezone'),
        )),
        ('instruments', Instrument, lambda r: Instrument(
            id=r['id'], name=r['name'],
            instrument_type=r.get('instrument_type'),
            aperture=r.get('aperture'), power=r.get('power'),
            eyepiece=r.get('eyepiece'),
        )),
        ('objects', Object, lambda r: Object(
            id=r['id'], name=r['name'],
            desination=r.get('desination'), type=r.get('type'),
            props=r.get('props'),
        )),
        ('sessions', Session, lambda r: Session(
            id=r['id'], number=r.get('number'),
            start_datetime=_parse_datetime(r.get('start_datetime')),
            end_datetime=_parse_datetime(r.get('end_datetime')),
            cloud_percentage=r.get('cloud_percentage'),
            cloud_type=r.get('cloud_type'),
            light_pollution=r.get('light_pollution'),
            limiting_magnitude=r.get('limiting_magnitude'),
            moon_phase=r.get('moon_phase'),
            moon_altitude=r.get('moon_altitude'),
            instrument=r.get('instrument'),
        )),
        ('observations', Observation, lambda r: Observation(
            id=r['id'], object=r.get('object'),
            place=r.get('place'), instrument=r.get('instrument'),
            session_id=r.get('session_id'),
            datetime=_parse_datetime(r.get('datetime')),
            observation=r.get('observation'),
            prop1=r.get('prop1'), prop1value=r.get('prop1value'),
        )),
    ]

    for key, model, factory in table_configs:
        added = 0
        skipped = 0
        for record in data.get(key, []):
            if mode == 'merge' and db.session.get(model, record['id']):
                skipped += 1
                continue
            db.session.add(factory(record))
            added += 1
        stats['added'][key] = added
        stats['skipped'][key] = skipped

    db.session.commit()
    return stats


@web.route('/backup')
@login_required
def backup_page():
    """Render the backup management page."""
    counts = {}
    try:
        counts = {
            'types': Type.query.count(),
            'properties': Property.query.count(),
            'places': Place.query.count(),
            'instruments': Instrument.query.count(),
            'objects': Object.query.count(),
            'sessions': Session.query.count(),
            'observations': Observation.query.count(),
        }
    except Exception as e:
        flash(f'Error loading counts: {str(e)}', 'danger')
    return render_template('backup/index.html', counts=counts)


@web.route('/backup/export')
@login_required
def backup_export():
    """Export all data as a downloadable JSON file."""
    try:
        data = _build_backup_data()
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f'astronomy_backup_{timestamp}.json'
        return Response(
            json_str,
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as e:
        flash(f'Error exporting data: {str(e)}', 'danger')
        return redirect(url_for('web.backup_page'))


@web.route('/backup/import', methods=['POST'])
@login_required
def backup_import():
    """Import (merge) data from an uploaded JSON file. Existing records are kept."""
    try:
        file = request.files.get('backup_file')
        if not file or file.filename == '':
            flash('No file selected.', 'warning')
            return redirect(url_for('web.backup_page'))

        raw = file.read()
        data = json.loads(raw)

        if not isinstance(data, dict) or 'version' not in data:
            flash('Invalid backup file format.', 'danger')
            return redirect(url_for('web.backup_page'))

        stats = _import_backup_data(data, mode='merge')
        total_added = sum(stats['added'].values())
        total_skipped = sum(stats['skipped'].values())
        flash(f'Import complete! Added {total_added} records, skipped {total_skipped} existing.', 'success')
    except json.JSONDecodeError:
        flash('File is not valid JSON.', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Error importing data: {str(e)}', 'danger')
    return redirect(url_for('web.backup_page'))


@web.route('/backup/restore', methods=['POST'])
@login_required
def backup_restore():
    """Restore data from an uploaded JSON file. WARNING: replaces all existing data."""
    try:
        file = request.files.get('backup_file')
        if not file or file.filename == '':
            flash('No file selected.', 'warning')
            return redirect(url_for('web.backup_page'))

        raw = file.read()
        data = json.loads(raw)

        if not isinstance(data, dict) or 'version' not in data:
            flash('Invalid backup file format.', 'danger')
            return redirect(url_for('web.backup_page'))

        stats = _import_backup_data(data, mode='restore')
        total_added = sum(stats['added'].values())
        flash(f'Restore complete! All previous data replaced. Loaded {total_added} records.', 'success')
    except json.JSONDecodeError:
        flash('File is not valid JSON.', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Error restoring data: {str(e)}', 'danger')
    return redirect(url_for('web.backup_page'))
'''
    
    with open('web_routes.py', 'w') as f:
        f.write(content)
    
    print("Created new web_routes.py with proper ID handling!")
    return True

if __name__ == '__main__':
    create_new_web_routes()